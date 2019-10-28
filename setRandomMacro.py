#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Set a macro to a random value.
Created as answer to https://stackoverflow.com/questions/58560480

Provide user from the commandline or from Env var support:
# export ZABBIX_SERVER='https://your_zabbix_host/zabbix/'
# export ZABBIX_USERNAME='admin'
# export ZABBIX_PASSWORD='secretPassword'


$ ./setRandomMacro.py -u admin -p zabbix -Z http://yourzabbix  -H yourHost -M '{$RANDOM}'
Connecting to http://yourzabbix
Host yourHost (Id: ----)
{$RANDOM}: current value "17" -> new value "356"


$ ./setRandomMacro.py -u admin -p zabbix -Z http://yourzabbix  -H yourHost -M '{$RANDOM}'
Connecting to http://yourzabbix
Host yourHost (Id: ----)
{$RANDOM}: current value "356" -> new value "72"
"""

from zabbix.api import ZabbixAPI

import json
import argparse
import getopt
import sys
import os
import random


# Class for argparse env variable support
class EnvDefault(argparse.Action):
    # From https://stackoverflow.com/questions/10551117/
    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required,
                                         **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def jsonPrint(jsonUgly):
    print(json.dumps(jsonUgly, indent=4, separators=(',', ': ')))


def ArgumentParser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-Z',
                        required=True,
                        action=EnvDefault,
                        envvar='ZABBIX_SERVER',
                        help="Specify the zabbix server URL ie: http://yourserver/zabbix/ (ZABBIX_SERVER environment variable)",
                        metavar='zabbix-server-url')

    parser.add_argument('-u',
                        required=True,
                        action=EnvDefault,
                        envvar='ZABBIX_USERNAME',
                        help="Specify the zabbix username (ZABBIX_USERNAME environment variable)",
                        metavar='Username')

    parser.add_argument('-p',
                        required=True,
                        action=EnvDefault,
                        envvar='ZABBIX_PASSWORD',
                        help="Specify the zabbix username (ZABBIX_PASSWORD environment variable)",
                        metavar='Password')

    parser.add_argument('-H',
                        required=True,
                        help="Hostname",
                        metavar='hostname')

    parser.add_argument('-M',
                        required=True,
                        help="Macro to set",
                        metavar='macro')
    return parser.parse_args()


def main(argv):

    # Parse arguments and build work variables
    args = ArgumentParser()
    zabbixURL = args.Z
    zabbixUsername = args.u
    zabbixPassword = args.p
    hostName = args.H
    macroName = args.M

    # API Connect
    print('Connecting to {}'.format(zabbixURL))
    zapi = ZabbixAPI(url=zabbixURL, user=zabbixUsername,
                     password=zabbixPassword)

    hostObj = zapi.host.get(search={'host': hostName}, output='hostids')
    print('Host {} (Id: {})'.format(hostName, hostObj[0]['hostid']))

    currentMacro = zapi.usermacro.get(
        hostids=hostObj[0]['hostid'], filter={'macro': macroName})

    if (currentMacro):
        newMacroValue = random.randint(1, 1001)
        print('{}: current value "{}" -> new value "{}"'.format(macroName,
                                                                currentMacro[0]['value'], newMacroValue))
        zapi.usermacro.update(
            hostmacroid=currentMacro[0]['hostmacroid'], value=newMacroValue)
    else:
        print('No {} macro found on host {}'.format(macroName, hostName))


if __name__ == "__main__":
    main(sys.argv[1:])
