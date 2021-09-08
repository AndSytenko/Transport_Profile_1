#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
jx library
'''

__author__ = 'oleg.larintsev@nokia.com'
__version__ = '0.1.0'

from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
#from jx.terminalcontroller import TerminalController
import re
import os
from termcolor import colored, cprint
#debugging = 1

# -----------------------------------------------
def debug(msg, flag = 0):
    if flag:
        cprint('{}'.format(msg), 'cyan')

def error(msg):
    cprint('{}'.format(msg), 'yellow', 'on_red')

def warning(msg):
    cprint('{}'.format(msg), 'yellow')

def info(msg):
    cprint('{}'.format(msg), 'green')

def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z

def str_norm(s):
    s= re.sub('<.*>','',s)
    return re.sub('\"','',s)

def print_config(tmpl, config, ntype='ds', filters=[]):
    # Create the jinja2 environment.
    env = Environment(loader=FileSystemLoader(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates/{}/".format(ntype)))),
                         trim_blocks=True)
    for f in filters:
        for fkey,fval in f.iteritems():
            env.filters[fkey] = fval
    jtmpl = env.get_template("{}.j2".format(tmpl))
    print(jtmpl.render(config))
