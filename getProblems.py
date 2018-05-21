#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Get current problems, print out some details
"""

from zabbix.api import ZabbixAPI

zabbixServer    = 'http://yousrserver/zabbix/'
zabbixUser      = 'someuser'
zabbixPass      = 'somepass'

zapi = ZabbixAPI(url=zabbixServer, user=zabbixUser, password=zabbixPass)

problems = zapi.problem.get()

for problem in problems:
    trigger = zapi.trigger.get (triggerids=problem['objectid'], selectHosts='extend')
    interface = zapi.hostinterface.get(hostids=trigger[0]['hosts'][0]['hostid'])
    group = zapi.hostgroup.get(hostids=trigger[0]['hosts'][0]['hostid'])

    enabled = "Enabled"
    if (trigger[0]['hosts'][0]['status'] == "1"):
        enabled = "Disabled"

    print "Group:{}; Host:{}; IP:{}; Problem:{}; {}".format(group[1]['name'],
                                                           trigger[0]['hosts'][0]['host'],
                                                           interface[0]['ip'],
                                                           trigger[0]['description'],
                                                           enabled )
