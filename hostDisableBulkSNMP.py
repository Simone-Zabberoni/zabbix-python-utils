#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Disable bulk SNMP on all existing hosts.
You can also filter with a dict:

    f  = {  'host' : 'somehostname'  }
    hosts = zapi.hostinterface.get(output=['hostids', 'host'], filter=f)

You can filter by name, template, group etc...

"""

from zabbix.api import ZabbixAPI

zabbixServer    = 'http://yousrserver/zabbix/'
zabbixUser      = 'someuser'
zabbixPass      = 'somepass'

zapi = ZabbixAPI(url=zabbixServer, user=zabbixUser, password=zabbixPass)

interfaces = zapi.hostinterface.get()

for interface in interfaces:
    if (interface['type'] == '2' ):
        print "Hostid: {} InterfaceID {} ".format(interface['hostid'], interface['interfaceid'])
        zapi.hostinterface.update(interfaceid=interface['interfaceid'], bulk='0')
