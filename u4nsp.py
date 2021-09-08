#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Generate SNMPv3 security keys and create SR OS config snippet for a certain user
SNMP account's data is read from the YAML config 'u4nsp.yaml'
Require 'snmpkey' from the Net::SNMP module (perl) ('libnet-snmp-perl' (debian)) 
'''

__author__ = 'oleg.larintsev@nokia.com'
__version__ = '0.0.1'
debugging = 1

import yaml
import getopt
import subprocess
import sys
import os
#import unicodedata
import re
from os.path import basename
from jxlib import *

def redopt():
    o = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi:y:",["id=", "yaml="])
    except getopt.GetoptError as e:
        error (str(e))
        usage()
        sys.exit(2)

    if not opts:
        usage()
        quit()

    for opt, arg in opts:
#        debug("opt: %s, arg: %s" % (opt, arg))
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ('-i', '--aggrs'):
            o['id'] = arg
        elif opt in ('-y', '--yaml'):
            o['yaml'] = arg

    if not 'id' in o:
        error('The \"-i\" switch is mandatory!')
        sys.exit(2)
    if not 'yaml' in o:
        error('The \"-y\" switch is mandatory!')
        sys.exit(2)
    return o

def usage ():
    info ("Usage: %s -i <SNMP engine id> -y <yaml config file> [-h]" % sys.argv[0])
    sys.exit(0)

if __name__ == '__main__':
    o = redopt()
    if not os.path.exists(os.path.abspath(o['yaml'])):
        error("Coudn't find config file \"{}\" !".format(o['yaml']))
        sys.exit(2)

    with open (os.path.abspath(o['yaml']), 'r') as f:
        try:
            cfg = yaml.load(f, Loader=yaml.FullLoader)
            debug (cfg, debugging)
#            print ("====================")
        except yaml.YAMLError as exc:
            print(exc)
        f.close()

    cmd = ["{}".format(cfg['snmpkey']), "sha", "{}".format(cfg['password']), "{}".format(o['id']), "des", "{}".format(cfg['password'])]
#    cmd = ["{}".format(snmpkey), "sha", "{}".format(password), "{}".format(o['id']), "des", "{}".format(password)]
    try:
#p = subprocess.Popen(["/usr/bin/snmpkey", "sha", "'@lcatel$NMP5620'", "0000197f00008c83dfbbee12", "des", "'@lcatel$NMP5620'"],stdout=subprocess.PIPE, stderr=subproce.STDOUT )
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except OSError:
        error (OSError)
        sys.exit(2)
    
    if p:
        cstdout = p.stdout.readlines()
        debug("{}".format(cstdout), debugging)
        
    nfmp_authKey = ''; nfmp_privKey = ''
    # Search for auth key
    ak = re.compile(r'^authKey: 0x(.*)\n')
    for l in cstdout:
        r  = ak.search(l.decode('utf-8'))
        if r and r.group(0) and r.group(1):
            nfmp_authKey = r.group(1)
            break

    # Search for priv key
    ak = re.compile(r'^privKey: 0x(.*)\n')
    for l in cstdout:
        r  = ak.search(l.decode('utf-8'))
        if r and r.group(0) and r.group(1):
            nfmp_privKey = r.group(1)
            break
    debug("Auth Key: {}".format(nfmp_authKey), debugging)
    debug("Priv Key: {}".format(nfmp_privKey), debugging)
    config = {}
    config['user'] = cfg['snmpuser']
    config['authKey'] = nfmp_authKey
    config['privKey'] = nfmp_privKey

    print_config("ks-nfmp-user", config)
