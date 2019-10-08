#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Get item names for a specific host

# export ZABBIX_SERVER='https://your_zabbix_host/zabbix/'
# export ZABBIX_PASSWORD='admin'
# export ZABBIX_USERNAME='secretPassword'

# ./getItems.py -H SomePrinter
Connecting to https://your_zabbix_host/zabbix/'
HostID: 10675 - Host: SomePrinter (192.168.10.20) - ItemID: 155278 - Item name: Device alert - Key: printer.alert
HostID: 10675 - Host: SomePrinter (192.168.10.20) - ItemID: 167937 - Item name: Device alert2 - Key: printer.alert2
HostID: 10675 - Host: SomePrinter (192.168.10.20) - ItemID: 135365 - Item name: Device Contact - Key: printer.device.contact
HostID: 10675 - Host: SomePrinter (192.168.10.20) - ItemID: 135366 - Item name: Device Description - Key: printer.device.description
HostID: 10675 - Host: SomePrinter (192.168.10.20) - ItemID: 135367 - Item name: Device Location - Key: printer.device.location
HostID: 10675 - Host: SomePrinter (192.168.10.20) - ItemID: 135368 - Item name: Device Model - Key: printer.device.model
HostID: 10675 - Host: SomePrinter (192.168.10.20) - ItemID: 135369 - Item name: Device Name - Key: printer.device.name
HostID: 10675 - Host: SomePrinter (192.168.10.20) - ItemID: 135370 - Item name: Device Serial - Key: printer.device.serial
HostID: 10675 - Host: SomePrinter (192.168.10.20) - ItemID: 135371 - Item name: Device Uptime - Key: printer.device.uptime
HostID: 10675 - Host: SomePrinter (192.168.10.20) - ItemID: 136890 - Item name: Supply TK-3190 Total - Key: printer.supplyTotal[1]
HostID: 10675 - Host: SomePrinter (192.168.10.20) - ItemID: 136892 - Item name: Supply TK-3190 Remaining (%) - Key: printer.supplyUsablePercent[1]
HostID: 10675 - Host: SomePrinter (192.168.10.20) - ItemID: 136894 - Item name: Supply TK-3190 Remaining - Key: printer.supplyUsable[1]

"""

from zabbix.api import ZabbixAPI

import sys
import os
import json
import argparse


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
                        help="Specify the hostname of the monitored device",
                        metavar='hostname')

    return parser.parse_args()


def main(argv):

    # Parse arguments and build work variables
    args = ArgumentParser()
    zabbixURL = args.Z
    zabbixUsername = args.u
    zabbixPassword = args.p
    hostName = args.H
    zabbixSearch = {'name': hostName}

    # API Connect
    print('Connecting to {}'.format(zabbixURL))
    try:
        zapi = ZabbixAPI(url=zabbixURL, user=zabbixUsername,
                         password=zabbixPassword)
    except Exception as e:
        print("Connection error:{}".format(str(e)))
        exit()

    try:
        hosts = zapi.host.get(search=zabbixSearch, output=[
                              'hostids', 'host', 'name'])
    except Exception as e:
        print("Host get error:{}".format(str(e)))
        exit()

    if (len(hosts) == 0):
        print("Can't find host {}".format(hostName))
        exit()

    for host in hosts:
        items = zapi.item.get(hostids=host['hostid'])
        for item in items:
            print("HostID: {} - Host: {} ({}) - ItemID: {} - Item name: {} - Key: {}".format(
                host['hostid'], host['name'], host['host'], item['itemid'], item['name'], item['key_']))


if __name__ == "__main__":
    main(sys.argv[1:])
