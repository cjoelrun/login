#!/usr/bin/env python

""" Log into Next-Generation compute nodes.

Usage:
  login.py <UUID> [--config=<file>]

Arguments:
  <UUID>  UUID of a Next-Gen instance.

Options:
  -h --help        Show this screen.
  --config=<file>  Path to your configuration file. [default: ~/.core.cfg]

"""
import configparser
from docopt import docopt
import os
import pexpect
import requests

def login(bastion, username, password, node):
    child = pexpect.spawn('ssh ' + username + '@' + bastion)
    child.expect(username + '@' + bastion + '\'s password:')
    child.sendline(password)

    child.expect('Log into: ')
    child.sendline(node)

    child.interact()

def parse_config(path):
    try:
        with open(os.path.expanduser(args['--config'])): pass
    except IOError:
        print "Cannot open configuration file."
        os._exit(0)
    
    config = configparser.RawConfigParser()
    config.read(path)

    return dict(config.items('login'))

def parse_node(raw):
    host = raw[0]['Instance_Data']['host']
    node = host[2:].replace('-', '.')
    
    return node

def search_ohthree(ohthree, regions, UUID):
    for i, e in enumerate(regions):
        url =  ohthree % (regions[i].strip().lower(), UUID)
        response = requests.get(url, verify = False)
        if response.status_code == requests.codes.ok:
            json = response.json()
        else:
            continue
    try:
        return json
    except:
        print "Unable to return JSON; Verify the UUID and ohthree URL."
        os._exit(0)

if __name__ == '__main__':
    args = docopt(__doc__, help = True)
    
    values = parse_config(os.path.expanduser(args['--config']))
    json = search_ohthree(values['ohthree'].strip('\''), values['regions'].split(','), args['<UUID>'])
    node = parse_node(json)

    login(values['bastion'].strip('\''), values['username'], values['password'], node)
