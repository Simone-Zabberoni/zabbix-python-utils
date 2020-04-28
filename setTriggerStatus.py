#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enable or disable by triggerid

python setTriggerStatus.py -Z http://somezabbix/ -u Admin -p somepassword -i "22321386 1232145 1234" -s 0

"""


from zabbix.api import ZabbixAPI
import logging
import json
import csv
import argparse
import getpass
import getopt
import re
import sys
import os


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

    parser.add_argument('-i',
                        required=True,
                        help="Trigger ID",
                        metavar='triggerid')

    parser.add_argument('-s',
                        required=True,
                        help="Status (0=on, 1=off)",
                        metavar='triggerstatus')

    return parser.parse_args()


def main(argv):

    # Parse arguments and build work variables
    args = ArgumentParser()
    zabbixURL = args.Z
    zabbixUsername = args.u
    zabbixPassword = args.p

    zapi = ZabbixAPI(url=zabbixURL, user=zabbixUsername,
                     password=zabbixPassword)

    params = []
    for triggerid in args.i.split(' '):
        trigObj = {"triggerid": triggerid, "status": args.s}
        params.append(trigObj)

    # Call request directly for the custom param field, instead of using zapi.trigger.update
    result = zapi.do_request('trigger.update', params=params)
    jsonPrint(result)


if __name__ == "__main__":
    main(sys.argv[1:])
