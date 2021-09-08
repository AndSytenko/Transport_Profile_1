#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Kyivsatr MEN-21 project
Build SR OS configs for all nodes from yaml data
'''

__author__ = 'oleg.larintsev@nokia.com'
__version__ = '0.2.5'

import yaml
import os
import getopt
from jinja2 import Environment, FileSystemLoader
import sys
from jxlib import *
from xlfilters import *

vDIR = os.path.dirname(os.path.abspath(__file__))

def print_config(jtmpl, _type='ds'):
    # Create the jinja2 environment.
    j2_env = Environment(loader=FileSystemLoader(os.path.join(vDIR, 'templates/{}'.format(_type))),
                         trim_blocks=True)
    j2_env.filters["ipv4_addr" ] = get_ipv4_from_ip_with_cidr
    j2_env.filters["str_match_rgx"] =  str_match_rgx
    j2_env.filters["modulo"] =  j_modulo
    j2_env.filters["last_nth_ip" ] = get_nth_last_ip
    j2_env.filters["first_nth_ip" ] = get_nth_ip
    return (j2_env.get_template(jtmpl).render(config))

def redopt():
    o = {}
    # Default options
    # Type - distribution switch
    o['type'] = 'ds'
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hp:c:t:o:",["params=","config=","type=","out="])
    except getopt.GetoptError as e:
        error (str(e))
        usage()
        sys.exit(2)
    if not opts:
        usage()
        quit()
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ('-p', '--params'):
            o['params']=arg
        elif opt in ('-c', '--config'):
            o['config']=arg
        elif opt in ('-t', '--type'):
            if arg in [ 'sr', 'ds']:
                o['type'] = arg
            else:
                usage()
                sys.exit()
        elif opt in ('-o', '--out'):
            o['out']=arg
    if not 'params' in o:
        error ('The \"-p\" switch is mandatory!')
        sys.exit(2)
    if not 'config' in o:
        error ('The \"-c\" switch is mandatory!')
        sys.exit(2)
    return o

def usage ():
    info ("Usage: %s -p <global params file> -c <config file> [-t <type: {ds*|sr}] [-o <output file>] [-h]" % sys.argv[0])
    sys.exit(2)

def save_config(_config, _out_file = None):
    if _out_file is None:
        out = sys.stdout
    else:
        out = open(_out_file, 'w')
    try:
        out.write(_config+"\n")
    except:
        error ("Unexpected error:", sys.exc_info()[0])
        raise
    finally:
        out.close()

if __name__ == '__main__':
    switches = redopt()
    #debug switches
    if not os.path.exists(os.path.abspath(switches['params'])):
        error ("Coudn't find the global parameter file \"{}\" !".format(switches['params']))
        sys.exit(2)
    if not os.path.exists(os.path.abspath(switches['config'])):
        error("Coudn't find the ring config file \"{}\" !".format(switches['config']))
        sys.exit(2)

    with open (os.path.abspath(switches['config']), 'r') as f:
        try:
            config = yaml.load(f, Loader=yaml.FullLoader)
#            print config
#            print "===================="
        except yaml.YAMLError as exc:
            error(exc)
            sys.exit(2)
    with open (os.path.abspath(switches['params']), 'r') as f:
        try:
            #params = yaml.load(f)
            params = yaml.load(f, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            error(exc)
            sys.exit(2)

    config = merge_dicts(config, params)
    #print_config(jxlib.merge_dicts(config, params))
    #print_config('ks-main.j2')

    if ('out' in switches.keys()):
        if not os.path.exists(os.path.dirname(os.path.abspath(switches['out']))):
            error("Coudn't find the output dir \"{}\" !".format(os.path.dirname(os.path.abspath(switches['out']))))
            sys.exit(2)
        save_config(print_config('ks-main.j2', switches['type']), os.path.abspath(switches['out']))
    else:
        save_config(print_config('ks-main.j2', switches['type']))

#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
