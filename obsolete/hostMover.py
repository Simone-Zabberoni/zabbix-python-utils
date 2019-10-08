#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Move hosts to a specific hostgroup list basing on a csv file
Please refer to README.md for hosts.csv syntax

"""

import csv
import json
from zabbix.api import ZabbixAPI

fileName        = 'hosts.csv'
zabbixServer    = 'http://yourserver/zabbix/'
zabbixUser      = 'someuser'
zabbixPass      = 'somepass'

zapi = ZabbixAPI(url=zabbixServer, user=zabbixUser, password=zabbixPass)


# Read CSV file
hostFile = open(fileName)
hostReader = csv.reader(hostFile, delimiter=';', quotechar='|')
# Uncomment if your csv has headers
#headers = hostReader.next()
hostData = list(hostReader)

# CSV Parsing
for host in hostData:
    wantedGroups        = []
    actualGroupIds      = []
    hostName            = host[1].split("-")[0]
    moveHost = False

    # Get Zabbixhost informations
    hostId = zapi.get_id('host', item=hostName, with_id=False, hostid=None)
    hostObj = zapi.host.get(hostids=hostId, selectGroups='extend')

    if hostId:
        # Create a comparison array of hostgroups id
        for hg in hostObj[0]['groups']:
            actualGroupIds.append(hg['groupid'])

        print "Working on " , hostName, " [id ", hostId,"]"

        for hostgroupName in host[0].split("-"):
            hostGroupId = zapi.get_id('hostgroup', item=hostgroupName, with_id=False, hostid=None)
            wantedGroups.append( {'groupid' : hostGroupId} )

            if str(hostGroupId) not in actualGroupIds:
                print "Hostgroup association missing: ", hostgroupName, " [id ", hostGroupId,"] "
                moveHost = True

        if moveHost:
            print "Setting hostgroups: ", wantedGroups
            zapi_result = zapi.host.update(hostid=hostId, groups=wantedGroups)
        else:
            print "Nothing to do"

    else:
        print "Host " + hostName + " does non exists"

    print "--------------------------------------------------------------------"
