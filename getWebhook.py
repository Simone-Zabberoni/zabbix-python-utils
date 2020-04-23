#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Get all webhooks, print the id and name (or extended info with -e)

You can provide an argument to filter a specific webhook
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

    parser.add_argument('-w',
                        required=False,
                        help="Webhook to search",
                        metavar='hostname')

    parser.add_argument('-e', action='store_true',
                        help="Extended output")

    return parser.parse_args()


def main(argv):

    # Parse arguments and build work variables
    args = ArgumentParser()
    zabbixURL = args.Z
    zabbixUsername = args.u
    zabbixPassword = args.p
    webhookFilter = args.w

    zapi = ZabbixAPI(url=zabbixURL, user=zabbixUsername,
                     password=zabbixPassword)

    if (webhookFilter):
        # Filter based on the cmdline argument
        f = {'name': webhookFilter}
        hosts = zapi.mediatype.get(
            search=f, output='extend', selectTags='extend')
    else:
        hosts = zapi.mediatype.get(output='extend')

    if (args.e):
        jsonPrint(hosts)
    else:
        for host in hosts:
            print("ID: {} - Host: {}".format(host['hostid'], host['host']))


if __name__ == "__main__":
    main(sys.argv[1:])
