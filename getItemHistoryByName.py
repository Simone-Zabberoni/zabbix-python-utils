#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
# export ZABBIX_SERVER='https://your_zabbix_host/zabbix/'
# export ZABBIX_PASSWORD='admin'
# export ZABBIX_USERNAME='secretPassword'

# ./getItemHistoryByName.py -H SomeHost -I "ICMP Loss" -f "13/8/2019 00:00" -t "13/8/2019 23:59" | head
Connecting to https://your_zabbix_host/zabbix/'
Host SomeHost (192.168.203.19):
ItemID: 158495 - Item: ICMP loss - Key: icmppingloss
1565676016 13/08/2019 08:00:16 Value: 0.0000
1565676076 13/08/2019 08:01:16 Value: 0.0000
1565676136 13/08/2019 08:02:16 Value: 0.0000
1565676196 13/08/2019 08:03:16 Value: 0.0000
1565676256 13/08/2019 08:04:16 Value: 0.0000
1565676316 13/08/2019 08:05:16 Value: 0.0000

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
                        required=True,
                        help="Specify the \"from\" date - format 26/6/2018 00:00",
                        metavar='from-date')

    parser.add_argument('-t',
                        required=True,
                        help="Specify the \"to\" date - format 26/6/2018 00:00",
                        metavar='to-date')

    parser.add_argument('-H',
                        required=True,
                        help="Specify the hostname of the monitored device",
                        metavar='hostname')

    parser.add_argument('-I',
                        required=True,
                        help="Specify the item name",
                        metavar='to-date')

    return parser.parse_args()


def main(argv):

    # Parse arguments and build work variables
    args = ArgumentParser()
    zabbixURL = args.Z
    zabbixUsername = args.u
    zabbixPassword = args.p
    itemName = args.I
    hostName = args.H

    hostFilter = {'name': hostName}
    itemFilter = {'name': itemName}

    # Convert from/to dates into timestamps
    fromTimestamp = time.mktime(datetime.datetime.strptime(
        args.f, "%d/%m/%Y %H:%M").timetuple())
    tillTimestamp = time.mktime(datetime.datetime.strptime(
        args.t, "%d/%m/%Y %H:%M").timetuple())

    # API Connect
    print('Connecting to {}'.format(zabbixURL))
    try:
        zapi = ZabbixAPI(url=zabbixURL, user=zabbixUsername,
                         password=zabbixPassword)
    except Exception as e:
        print("Connection error: {}".format(str(e)))
        exit()

    # Search the hostname
    try:
        hosts = zapi.host.get(filter=hostFilter, output=[
                              'hostids', 'host', 'name'])
    except Exception as e:
        print("Host get error:{}".format(str(e)))
        exit()

    if (len(hosts) == 0):
        print("Can't find host {}".format(hostName))
        exit()

    # Search the item object
    try:
        items = zapi.item.get(filter=itemFilter, host=hosts[0]['host'],
                              output='extend', selectHosts=['host', 'name'])
    except Exception as e:
        print("Get item error: {}".format(str(e)))
        exit()

    print("Host {} ({}):".format(hosts[0]['name'], hosts[0]['host']))
    # for loop - future fuzzy search
    for item in items:
        print(
            "ItemID: {} - Item: {} - Key: {}".format(item['itemid'], item['name'], item['key_']))

        # Search values
        try:
            values = zapi.history.get(
                itemids=item['itemid'], time_from=fromTimestamp, time_till=tillTimestamp, history=item['value_type'])
        except Exception as e:
            print("Values get error: {}".format(str(e)))
            continue

        # Convert date/timestamp and print values
        for historyValue in values:
            currentDate = datetime.datetime.fromtimestamp(
                int(historyValue['clock'])).strftime('%d/%m/%Y %H:%M:%S')

            print("{} {} Value: {}".format(
                historyValue['clock'], currentDate, historyValue['value']))


if __name__ == "__main__":
    main(sys.argv[1:])
