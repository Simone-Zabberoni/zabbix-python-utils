#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enable automatic inventory on all existing hosts.
You can also filter with a dict:

    f  = {  'host' : 'somehostname'  }
    hosts = zapi.host.get(output=['hostids', 'host'], filter=f)

You can filter by name, template, group etc...

"""

from zabbix.api import ZabbixAPI

zabbixServer    = 'http://yourserver/zabbix/'
zabbixUser      = 'someuser'
zabbixPass      = 'somepass'

zapi = ZabbixAPI(url=zabbixServer, user=zabbixUser, password=zabbixPass)

hosts = zapi.host.get(output=['hostids', 'host'])

for host in hosts:
    # Enable automatic inventory
    res = zapi.host.update(hostid=host['hostid'], inventory_mode=1)
    print res
