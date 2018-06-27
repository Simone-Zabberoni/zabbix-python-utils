#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Get item names for a specific host

# ./getItems.py some-host | grep ICMP
HostID: 12556 - Host: some-host - ItemID: 267223 - Item: ICMP ping - Key: icmpping
HostID: 12556 - Host: some-host - ItemID: 267224 - Item: ICMP loss - Key: icmppingloss
HostID: 12556 - Host: some-host - ItemID: 267225 - Item: ICMP response time - Key: icmppingsec
"""

from zabbix.api import ZabbixAPI
import sys

zabbixServer    = 'http://yourserver/zabbix/'
zabbixUser      = 'someuser'
zabbixPass      = 'somepass'

zapi = ZabbixAPI(url=zabbixServer, user=zabbixUser, password=zabbixPass)

if (sys.argv[1:]):
    # Filter based on the cmdline argument
    f  = {  'host' : sys.argv[1:]  }
    hosts = zapi.host.get(filter=f, output=['hostids', 'host'] )

    for host in hosts:
        items = zapi.item.get(hostids=host['hostid'])
        for item in items:
            print "HostID: {} - Host: {} - ItemID: {} - Item: {} - Key: {}".format(host['hostid'], host['host'], item['itemid'], item['name'], item['key_'])
else:
    print "Provide an hostname"
