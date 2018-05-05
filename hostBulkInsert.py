
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
From a single csv file:
- create hostgroups
- create hosts and
    - assign the correct interface
    - assign them to their correct groups
    - link them to the correct templates

Please refer to README.md for hosts.csv syntax

"""
import csv
from zabbix.api import ZabbixAPI

fileName        = 'hosts.csv'
zabbixServer    = 'http://yousrserver/zabbix/'
zabbixUser      = 'someuser'
zabbixPass      = 'somepass'



hostGroupNames  = []    
templateNames   = []

hostGroupId     = {}    
templateId      = {}

# Static values from zabbix api
interfaceType = {
            'agent' : 1,
            'SNMP'  : 2,
            'IMPI'  : 3,
            'JMX'   : 4
        }

#
zapi = ZabbixAPI(url=zabbixServer, user=zabbixUser, password=zabbixPass)

# Read CSV file
hostFile = open(fileName)
hostReader = csv.reader(hostFile, delimiter=';', quotechar='|')
# Uncomment if your csv has headers
#headers = hostReader.next() 
hostData = list(hostReader)


# Read all host groups and templates
for host in hostData:
    for hostgroupName in host[0].split("-"):
        hostGroupNames.append(hostgroupName)

    for templateName in host[3].split("-"):
        if templateName != 'DO_NOT_ADD':
            templateNames.append(templateName)


# Foreach UNIQUE hostgroup, create if missing
for hostgroupName in set(hostGroupNames):
    if (zapi.get_id('hostgroup', item=hostgroupName, with_id=False, hostid=None) == None):
        zapi.hostgroup.create(name=hostgroupName);
    # Create associative array Name=>Id
    hostGroupId[hostgroupName] = zapi.get_id('hostgroup', item=hostgroupName, with_id=False, hostid=None)

# Foreach UNIQUE template
for templateName in set(templateNames):
    # TODO : what if template does not exist ?
    # Create associative array Name=>Id
    templateId[templateName] = zapi.get_id('template', item=templateName, with_id=False, hostid=None)




# Create objects and add hosts
for host in hostData:
    h_groups            = []
    h_templates         = []
    h_name              = host[1]
    h_desc              = host[1]
    h_ip                = host[2]
    h_interfaces        = []

    if (host[3] == 'DO_NOT_ADD'):
        print 'Server : ' + h_name
    else:

        print 'DEVICE : ' + h_name

        # Build interface object
        for interface in host[4].split("-"):
            if (interfaceType[interface] == 1):
                port=10050
            else:
                port=161

            h_interfaces.append( {
                        'type' : interfaceType[interface],
                        'main' : 1,
                        'useip': 1,
                        'ip'   : h_ip,
                        'dns'  : "",
                        'port' : port
                    } )

        # Build hostgroup object
        for hostgroup in host[0].split("-"):
            h_groups.append( {
                        'groupid' : hostGroupId[hostgroup],
                    } )

        # Build template object
        for template in host[3].split("-"):
            h_templates.append( {
                        'templateid' : templateId[template],
                    } )

        print 'HOST ' + h_name

        print 'Interfaces '
        print  h_interfaces
        print 'HGroups '
        print h_groups
        print 'Templates'
        print h_templates

        # Add the host
        zapi_result = zapi.host.create(host=h_name, description=h_desc, interfaces=h_interfaces, groups=h_groups, templates=h_templates)
        print 'Add result'
        print zapi_result
        print '-------------------'
