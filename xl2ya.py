#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Convers csv files (KS MEN21 project) into a yaml variable structure
'''

__author__ = 'oleg.larintsev@nokia.com'
__version__ = '0.1.2'

import yaml
import getopt
import sys
import os
import unicodedata
import re
from os.path import basename
from jxlib import *
debugging = 1

def redopt():
    o = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:],"ha:r:n:i:y:",["aggrs=","rings=","nodes=", "index=", "yaml="])
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
        elif opt in ('-a', '--aggrs'):
            o['aggrs'] = arg
        elif opt in ('-r', '--rings'):
            o['rings'] = arg
        elif opt in ('-n', '--nodes'):
            o['nodes'] = arg
        elif opt in ('-i', '--index'):
            o['index'] = arg
        elif opt in ('-y', '--yaml'):
            o['yaml'] = arg

    if not 'aggrs' in o:
        error('The \"-a\" switch is mandatory!')
        sys.exit(2)
    if not 'rings' in o:
        error('The \"-r\" switch is mandatory!')
        sys.exit(2)
    if not 'nodes' in o:
        error('The \"-n\" switch is mandatory!')
        sys.exit(2)
    if not 'index' in o:
        error('The \"-i\" switch is mandatory!')
        sys.exit(2)
    try:
        int(o['index'])
    except ValueError:
        error("Index must be number!")
        sys.exit(2)
    return o

def usage ():
    info ("Usage: %s -a <aggregtion routers file> -n <ds nodes file> -r <rings file> -i <ring index> [-h]" % sys.argv[0])
    sys.exit(2)

def proc_dsnodes_list(_nodes_list):
    xp = []
    #               0     1   2      3     4      5      6      7       8
    #    <U+FEFF>#;Ring;Site;Node;System;N-SID;SBFD ID;Aggr;OSPF Area;SDP ID
    #    1;1;AGG_KIE799;ds1-ua0799;172.25.0.1;1001;524801;kie3;210;13001

    rw = re.compile('^(\s+)?(\<|\*+|=+|^Port|Id|\-+|$)')
    with open(_nodes_list, "r") as f:
        for line in f:
#            print("DS LINE: {}".format(line))
#            r = rw.search(line)
#            if not r:
#                #z = re.split(';', remove_control_chars(line.rstrip()), 10)
            z = re.split(';', str_norm(line.rstrip().lstrip()), 10)
            xp.append (z)
    return xp

def proc_rings_list(_rings_list):
    rl = []
    with open(_rings_list, "r") as f:
        for i, l in enumerate(f):
            if i == 0:
                continue
#            print("i: {}; Ring LINE: {}".format(i, l))
            l = re.split(';', str_norm(l.rstrip().lstrip()), 13)
            rl.append (l)
    return rl

def proc_aggrs_list(_rings_list):
    al = []
    with open(_rings_list, "r") as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
#            print("i: {}; Aggr LINE: {}".format(i, line))
#            r = rw.search(line)
#            if not r:
#                #z = re.split(';', remove_control_chars(line.rstrip()), 10)
            line = re.split(';', str_norm(line.rstrip().lstrip()), 10)
            al.append (line)
    f.close()
    return al

def get_chassis(_type):
    sp = re.compile(r'7750')
    r = sp.search(_type)
    if r:
        return 7750
    sp = re.compile(r'7250')
    r = sp.search(_type)
    if r:
        return 7250

def get_timos_version(_timos):
    debug("Timos str in: {}".format(_timos), debugging)
    vs = '0.0.0'; v = {}
    v['full'] = ''; v['major'] = 0;  v['minor'] = 0;  v['release'] = 0;
    sp = re.compile(r'[tT][iI][mM][oO][sS](?=\-[a-zA-Z]+\-)(\d+)\.(\d+)\.(.*)|(?!\-[a-zA-Z]+\-)(\d+)\.(\d+)\.(.*)')
    r = sp.search(_timos.strip('\ '))
    if r and r.group(0):
        vs = r.group(0)
    v['full'] = vs.strip('\ ')
    v['major'] = vs.split('.')[0]
    va = vs.split('.')
    if len(va) > 2:
        v['minor'] = va[1]
        v['release'] = va[2]
    return v

def save_yaml(_routers, out_yaml = None):
    if out_yaml is None:
        out = sys.stdout
    else:
        out = open(out_yaml, 'w')
    try:
        d = yaml.dump(_routers, out, default_flow_style=False)
    finally:
        if out_yaml is not None:
            out.close()

if __name__ == '__main__':
    o = redopt()

    if not os.path.exists(os.path.abspath(o['aggrs'])):
        error("Coudn't find aggrs file \"{}\" !".format(o['aggrs']))
        sys.exit(2)

    if not os.path.exists(os.path.abspath(o['rings'])):
        error("Coudn't find rings file \"{}\" !".format(o['rings']))
        sys.exit(2)

    if not os.path.exists(os.path.abspath(o['nodes'])):
        error("Coudn't find nodes file \"{}\" !".format(o['nodes']))
        sys.exit(2)

# DS Node List
nl = proc_dsnodes_list(o['nodes'])

# Ring list
rl = proc_rings_list(o['rings'])

# Aggr node List
al = proc_aggrs_list(o['aggrs'])

ksnodes = []
nodes_in_a_ring = []
aggrs_in_a_ring = []

# aggregators list
aggrs = []
# Aggr routers structured data
daggr = {}
a_header_map = [ 'id', 'ip', 'name', 'sid', 'sbfd', 'chassis', 'sros', 'sdpid' ]
# Convert aggr_nodes list into dict
for a in al:
###    0      1               2        3      4         5            6
### ['1', '172.16.252.1', 'sr1-kie2', '1', '524288', '7750-SR12', 'TiMOS-C-19.10.R6', 1001]
###   id      system_ip     name      sid   bfd        chassis      SROS              sdpid
#
    if not (a[2]):
        continue
    data =  (dict(zip(a_header_map,a)))
#    daggr[a[2]] = { 'id' : a[0], 'ip' : a[1], 'sid' : a[3], 'bfd': a[4], 'chassis': a[5], 'os': a[6] }
    daggr[a[2]] = data
    debug ("AGGR data: {}".format(data), debugging)
al = ''

# Fill DS node routers data struct for a ring N from the DS node list
# Parse DS nodes data
for i, n in enumerate(nl):
    #  0     1        2          3             4            5       6        7       8          9
    # '72', '12', 'UA0891', 'ds2-ua0891', '172.25.1.35', '4387', '525092', 'kie2', '106',     '13001'
    # 'id', 'ring #', 'site', 'node',      'system_ip',  'nsid', 'sbfd',  'aggr', 'ospf_area', 'sdp_id'

    if i == 0:
        continue
    y = {}
    y['bfd'] = {}
    y['ospf'] = []
    y['interfaces'] = []
    y['ports'] = []
    if int(n[1]) == int(o['index']):
        if not (n[3] in nodes_in_a_ring):
            nodes_in_a_ring.append(n[3])
        xn = {n[3] : {}}
        y['bfd']['discriminator'] = int(n[6])
        #y['ospf'].append({'type' : 'nssa', 'area' : int(n[8]) })
        y['ospf'].append({ 'area' : int(n[8]) })
        y['sdp'] = int(n[9])
        y['interfaces'].append( {'name': 'system', 'sid': int(n[5]), 'ip': "{}/32".format(n[4]), 'vlan': None, 'port': 'system', 'ospf_area': int(n[8])} )
        ksnodes.append({n[3]: y})
        print("Node: {}; IP: {}".format(n[3],n[4]))

ri = 0
# Fill DS node routers data struct for the ring N from the Ring list
# Parse ring data
for r in rl:
    debug("Ring: {}".format(r), debugging)
##    0      1          2           3             4           5          6            7               8           9            10            11     12
##  Ring   Site #    Node #       Site        Node          Peer        Port        Peer port    Port Media       SFP       Interface       OSPF     IP (/31)
## ['25',   '1',      '1',      'KIE3',     'sr1-kie3',   'ds1-ua0747', '', '       1/1/31',    '10GBASE-LR',   'SFP+',   'ds1-ua0747_if1', '210', '172.24.0.144;']
## ['25',   '2',      '2',      'UA0747',   'ds1-ua0747', 'sr1-kie3',   '1/1/31',   '0',        '10GBASE-LR',   'SFP+',   'sr1-kie3_if1',   '210', '172.24.0.145;']

    if int(r[0]) == int(o['index']):
        if (ri % 2) == 0:
            _srlg = "SRLG-ACW"
        else:
            _srlg = "SRLG-CW"
        if not (r[4] in nodes_in_a_ring):
            info("Node \"{}\" is not known: aggregator?".format(r[4]))
            # If a node is not one of DS node check the Aggr list data
            if r[4] in daggr:
                # It is - check if it's known yet
                if r[4] not in aggrs_in_a_ring:
                    # Not known -> create a base structure for a node
                    y = {}
                    y['bfd'] = {}
                    y['ospf'] = []
                    y['interfaces'] = []
                    y['ports'] = []
                    y['chassis'] = "{}".format(get_chassis(daggr[r[4]]['chassis']))
                    y['timos'] = get_timos_version(daggr[r[4]]['sros'])
                    y['bfd']['discriminator'] = int(daggr[r[4]]['sbfd'])
                    #y['ospf'].append({'type' : 'nssa', 'area' : int(r[11]) })
                    y['ospf'].append({ 'area' : int(r[11]) })
                    y['ports'].append( {'port': r[6], 'peer_name': r[5], 'peer_port': r[7], 'sfp': r[9]})
                    y['interfaces'].append( { 'name': 'system', 'sid': int(daggr[r[4]]['sid']), 'ip': "{}/32".format(daggr[r[4]]['ip']), 'vlan': None, 'port': 'system', 'ospf_area': 0 } )
                    y['interfaces'].append( { 'name' : "{}_if1".format(r[5]), 'port': r[6], 'vlan': 1, 'ip' : "{}/31".format(r[12]), 'ospf_area': int(r[11]), 'srlg': _srlg} )
                    # Append a ring data to a node (aggr) data struct
                    aggrs.append({r[4]: y})
                    aggrs_in_a_ring.append(r[4])
            else:
                warning ("Node {} is not defined!".format(r[4]))

        else:
            print("Node: {}: ".format(r[4]))
            #print nodes_in_a_ring.index(r[3])
            print ("@@ {} @@".format (ksnodes[nodes_in_a_ring.index(r[4])][r[4]]))
            ##ksnodes[nodes_in_a_ring.index(r[2])][r[2]]['ospf'].append({'type' : 'nssa', 'area' : int(n[8]) })
            # Check SFP: QSFP28?
            if r[9] == "QSFP28":
                ksnodes[nodes_in_a_ring.index(r[4])][r[4]]['ports'].append( {'port': r[6], 'peer_name': r[5], 'peer_port': r[7], 'sfp': r[9]})
                ksnodes[nodes_in_a_ring.index(r[4])][r[4]]['ports'].append( {'port': "{}/1".format(r[6]), 'peer_name': r[5], 'peer_port': "{}/1".format(r[7]), 'sfp': "CON"})
                ksnodes[nodes_in_a_ring.index(r[4])][r[4]]['interfaces'].append( { 'name' : "{}_if1".format(r[5]), 'port': "{}/1".format(r[6]), 'vlan': 1, 'ip' : "{}/31".format(r[12]), 'ospf_area': int(r[11]), 'srlg': _srlg} )
            else:
                ksnodes[nodes_in_a_ring.index(r[4])][r[4]]['ports'].append( {'port': r[6], 'peer_name': r[5], 'peer_port': r[7], 'sfp': r[9]})
                ksnodes[nodes_in_a_ring.index(r[4])][r[4]]['interfaces'].append( { 'name' : "{}_if1".format(r[5]), 'port': r[6], 'vlan': 1, 'ip' : "{}/31".format(r[12]), 'ospf_area': int(r[11]), 'srlg': _srlg} )

        ri += 1
        #print ("Incr: {}".format(ri))

#print ksnodes
routers = {}
ds = { 'ds': ksnodes }
aggr = {'aggr' : {} }
#routers = { 'ds' : ksnodes, 'aggr' : {} }
routers = { 'routers' : { 'ds' : ksnodes, 'aggr' : aggrs } }
#print (routers)

if 'yaml' in o:
    save_yaml(routers, o['yaml'])
else:
    save_yaml(routers)

#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
