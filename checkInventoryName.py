#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Check all hosts and return host name <-> inventory name matching
"""

from zabbix.api import ZabbixAPI

zabbixServer    = 'http://yourserver/zabbix/'
zabbixUser      = 'someuser'
zabbixPass      = 'somepass'


zapi = ZabbixAPI(url=zabbixServer, user=zabbixUser, password=zabbixPass)

hosts = zapi.host.get(selectInventory='extend', output=['hostids', 'host'])

for host in hosts:
    if (host['inventory']['name']):
        if (host['inventory']['name'] is not host['host']):
            print "Mismatch on id {}: Host Name: {} - SNMP Inventory Name: {} ".format(host['hostid'], host['host'],  host['inventory']['name'])
        else:
            print "Matching inventory name on id {}: Host Name: {}".format(host['hostid'], host['host'],  host['inventory']['name'])
    else:
         print "Missing inventory name on id {}: Host Name: {}".format(host['hostid'], host['host'],  host['inventory']['name'])


