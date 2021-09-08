#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
My handy lib
'''

__author__ = 'oleg.larintsev@nokia.com'
__version__ = '0.0.3'

from netaddr import *
import re
import sys

def get_nth_ip (netw, n=1):
    try:
        ipnet = IPNetwork(netw)
        if n < len(ipnet):
            return ipnet[n]
        else:
            return ipnet[0]
    except:
        print(sys.exc_info())

def get_nth_last_ip (netw, n=1):
    try:
        ipnet = IPNetwork(netw)
        if n < len(ipnet):
            return ipnet[len(ipnet)-2-n]
        else:
            return ipnet[len(ipnet)-2]
    except:
        print(sys.exc_info())

def get_ipv4_from_ip_with_cidr (netw):
    try:
        ipnet = IPNetwork(netw)
        return "{}".format(ipnet.ip)
    except:
        print(sys.exc_info())

def str_match_rgx(instr, rgx):
    rgx = r'{}'.format(rgx)
    rw = re.compile(rgx)
    return rw.search(instr)

def j_modulo(a, b):
    m = -1
    try:
        m = int(a) % int(b)
        return m
    except:
        print(sys.exc_info())


