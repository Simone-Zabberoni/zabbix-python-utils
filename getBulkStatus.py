#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
# export ZABBIX_SERVER='https://your_zabbix_host/zabbix/'
# export ZABBIX_PASSWORD='admin'
# export ZABBIX_USERNAME='secretPassword'

# ./getBulkStatus.py
HostID: 14062 - IP: 10.15.78.254 - Type: SNMP - Bulk: OFF
HostID: 13206 - IP: 10.4.25.25 - Type: SNMP - Bulk: OFF
HostID: 14063 - IP: 10.2.204.3 - Type: agent - Bulk: ON
HostID: 12643 - IP: 10.10.4.1 - Type: SNMP - Bulk: OFF
HostID: 14064 - IP: 172.30.11.11 - Type: agent - Bulk: ON
HostID: 14064 - IP: 172.30.11.15 - Type: SNMP - Bulk: OFF
HostID: 14065 - IP: 192.168.4.5 - Type: agent - Bulk: ON

# ./getBulkStatus.py SomeHost
HostID: 14065 - IP: 192.168.4.5 - Type: agent - Bulk: ON


# ./getBulkStatus.py AnotherHost | grep SNMP  | grep ON
HostID: 13818 - IP: 10.20.180.14 - Type: SNMP - Bulk: ON
"""

from zabbix.api import ZabbixAPI
import sys
import argparse
import time
import datetime
import os
import json

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

    parser.add_argument('-f',
                        required=False,
                        help="Hostname to search",
                        metavar='hostname')

    return parser.parse_args()


def main(argv):
    # Parse arguments and build work variables
    args = ArgumentParser()
    zabbixURL = args.Z
    zabbixUsername = args.u
    zabbixPassword = args.p
    hostNameFilter = args.f

    interfaceType = {
        '1': 'agent',
        '2': 'SNMP',
        '3': 'IPMI',
        '4': 'JMX',
    }

    bulkStatus = {
        '0': 'OFF',
        '1': 'ON',
    }

    zapi = ZabbixAPI(url=zabbixURL, user=zabbixUsername,
                     password=zabbixPassword)

    if (hostNameFilter):
        # Filter based on the cmdline argument
        f = {'host': hostNameFilter}
        hosts = zapi.host.get(search=f, output='extend', selectTags='extend')
        interfaces = zapi.hostinterface.get(hostids=hosts[0]['hostid'])
    else:
        interfaces = zapi.hostinterface.get()

    for interface in (interfaces):
        print('HostID: {} - IP: {} - Type: {} - Bulk: {}'.format(
            interface['hostid'], interface['ip'], interfaceType[interface['type']], bulkStatus[interface['bulk']]))


if __name__ == "__main__":
    main(sys.argv[1:])
