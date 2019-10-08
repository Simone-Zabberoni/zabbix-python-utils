#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

# export ZABBIX_SERVER='https://your_zabbix_host/zabbix/'
# export ZABBIX_PASSWORD='admin'
# export ZABBIX_USERNAME='secretPassword'

# ./getItemTrendByName.py  -I 'Page count (BW)' -f "1/2/2019 00:00" -t "28/2/2019 18:00" -H SomePrinter
Connecting to https://your_zabbix_host/zabbix/'
Host SomePrinter (192.168.203.19):
ItemID: 113312 - Item: Page count (BW) - Key: printer.pgBW
1549029600 01/02/2019 15:00:00 Value: Min: 15523 - Max: 15523 - Avg: 15523
1549033200 01/02/2019 16:00:00 Value: Min: 15523 - Max: 15531 - Avg: 15525
1549036800 01/02/2019 17:00:00 Value: Min: 15531 - Max: 15531 - Avg: 15531
1549263600 04/02/2019 08:00:00 Value: Min: 15532 - Max: 15532 - Avg: 15532
1549267200 04/02/2019 09:00:00 Value: Min: 15538 - Max: 15538 - Avg: 15538

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
            values = zapi.trend.get(
                itemids=item['itemid'], time_from=fromTimestamp, time_till=tillTimestamp, history=item['value_type'])
        except Exception as e:
            print("Values get error: {}".format(str(e)))
            continue

        # Convert date/timestamp and print values
        for trendValue in values:
            currentDate = datetime.datetime.fromtimestamp(
                int(trendValue['clock'])).strftime('%d/%m/%Y %H:%M:%S')

            print("{} {} Value: Min: {} - Max: {} - Avg: {}".format(
                trendValue['clock'], currentDate, trendValue['value_min'], trendValue['value_max'], trendValue['value_avg'],))


if __name__ == "__main__":
    main(sys.argv[1:])
