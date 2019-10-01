#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Get trend values (min/max/avg) for specific items in a time range:

# ./getItemTrendByName.py -H some-host  -I "ICMP Loss" -f "26/6/2018 00:00" -t "27/6/2018 23:59"
ItemID: 77012 - Item: ICMP loss - Key: icmppingloss
1529964000 26/06/2018 00:00:00 Value: Min: 0.0000 - Max: 100.0000 - Avg: 6.6667
1529967600 26/06/2018 01:00:00 Value: Min: 0.0000 - Max: 0.0000 - Avg: 0.0000
1529971200 26/06/2018 02:00:00 Value: Min: 0.0000 - Max: 0.0000 - Avg: 0.0000
[cut]

"""

from zabbix.api import ZabbixAPI
import sys
import argparse
import time
import datetime


zabbixServer = 'http://yourserver/zabbix/'
zabbixUser = 'someuser'
zabbixPass = 'somepass'


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', required=True, metavar='Hostname')
    parser.add_argument('-I', required=True, metavar='Item Name')
    parser.add_argument('-f', required=True, metavar='From Timestamp')
    parser.add_argument('-t', required=True, metavar='Till Timestamp')

    args = parser.parse_args()

    zapi = ZabbixAPI(url=zabbixServer, user=zabbixUser, password=zabbixPass)

    fromTimestamp = time.mktime(datetime.datetime.strptime(
        args.f, "%d/%m/%Y %H:%M").timetuple())
    tillTimestamp = time.mktime(datetime.datetime.strptime(
        args.t, "%d/%m/%Y %H:%M").timetuple())

    f = {'name': args.I}
    items = zapi.item.get(filter=f, host=args.H, output='extend')

    for item in items:
        print "ItemID: {} - Item: {} - Key: {}".format(item['itemid'], item['name'], item['key_'])

        values = zapi.trend.get(
            itemids=item['itemid'], time_from=fromTimestamp, time_till=tillTimestamp, history=item['value_type'])

        for historyValue in values:
            currentDate = datetime.datetime.fromtimestamp(
                int(historyValue['clock'])).strftime('%d/%m/%Y %H:%M:%S')

            print "{} {} Value: Min: {} - Max: {} - Avg: {}".format(historyValue['clock'], currentDate, historyValue['value_min'], historyValue['value_max'], historyValue['value_avg'],)


if __name__ == "__main__":
    main(sys.argv[1:])
