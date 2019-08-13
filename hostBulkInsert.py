#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
From a single csv file:
- create hostgroups
- create hosts and
    - assign the correct interface
    - assign them to their correct groups
    - link them to the correct templates
    - link them to the correct proxy

Env var support:
# export ZABBIX_SERVER='https://your_zabbix_host/zabbix/'
# export ZABBIX_PASSWORD='admin'
# export ZABBIX_USERNAME='secretPassword'


# ./hostBulkInsert.py -f HOSTS.csv      <- stops if hits an existing host
# ./hostBulkInsert.py -f HOSTS.csv -s   <- skips existing hosts


Csv file sample (see README for more):

Hostname; IP Address; Groups; Tags; Description; ICMP; SNMP community; Proxy; Templates; Interfaces
SomeHost;8.8.8.8;Group1-Group2-Routers;TagName=someValue;Device Description;snmpCommnity;ZabbixProxyName;Template Net Cisco IOS SNMPv2;agent-SNMP
SecondHost;8.8.8.8;Group3-Group2-SiteA;FirstTag=value,TagName=anotherValue;Device Description;snmpCommnity;;Template Net Cisco IOS SNMPv2;agent-SNMP

"""

from zabbix.api import ZabbixAPI

import json
import csv
import argparse
import getpass
import getopt
import re
import sys
import os


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
                        help="CSV filename to ingest",
                        metavar='csv-file-to-check')

    parser.add_argument('-s', action='store_true',
                        help="Skip existing hosts")
    return parser.parse_args()


def parseCSV(fileName, delimiter):
    data = []

    fileHandle = open(fileName)
    reader = csv.DictReader(fileHandle, delimiter=delimiter)
    for row in reader:
        data.append(row)
    return data


def main(argv):
    print('-- Host Bulk Insert --')

    # Parse arguments and build work variables
    args = ArgumentParser()
    zabbixURL = args.Z
    zabbixUsername = args.u
    zabbixPassword = args.p
    csvFile = args.f

    hostGroupNames = []
    templateNames = []
    proxyNames = []

    hostGroupId = {}
    templateId = {}
    proxyId = {}

    # Static values from zabbix api
    interfaceType = {
        'agent': 1,
        'SNMP': 2,
        'IMPI': 3,
        'JMX': 4
    }

    print('Reading CSV file: {}'.format(csvFile))
    hostData = parseCSV(csvFile, ';')
    # jsonPrint(hostData)

    # API Connect
    print('Connecting to {}'.format(zabbixURL))
    zapi = ZabbixAPI(url=zabbixURL, user=zabbixUsername,
                     password=zabbixPassword)

    print('Parsing templates, proxy and hostgroups')

    # Read all host groups and templates
    for host in hostData:
        for hostgroupName in host['Groups'].split("-"):
            hostGroupNames.append(hostgroupName)

        for templateName in host['Templates'].split("-"):
            if templateName != 'DO_NOT_ADD':
                templateNames.append(templateName)

        if len(host['Proxy']) > 0:
            proxyNames.append(host['Proxy'])

    print('Templates: {}'.format(set(templateNames)))
    print('Hostgroups: {}'.format(set(hostGroupNames)))
    print('Proxyes: {}'.format(set(proxyNames)))

    # Foreach UNIQUE hostgroup, create if missing
    for hostgroupName in set(hostGroupNames):
        if (zapi.get_id('hostgroup', item=hostgroupName, with_id=False, hostid=None) == None):
            print('Creating missing hostgroup: {}'.format(hostgroupName))
            zapi.hostgroup.create(name=hostgroupName)
        # Create associative array Name=>Id
        hostGroupId[hostgroupName] = zapi.get_id(
            'hostgroup', item=hostgroupName, with_id=False, hostid=None)

    # Foreach UNIQUE template
    for templateName in set(templateNames):
        # TODO : what if template does not exist ?
        # Create associative array Name=>Id
        templateId[templateName] = zapi.get_id(
            'template', item=templateName, with_id=False, hostid=None)

    # Foreach UNIQUE proxy
    for proxyName in set(proxyNames):
        # TODO : what if proxy does not exist ?
        # Create associative array Name=>Id

        f = {'host': proxyName}
        proxyObj = zapi.proxy.get(filter=f)
        proxyId[proxyName] = proxyObj[0]['proxyid']

    # Create objects and add hosts
    for host in hostData:
        h_groups = []
        h_templates = []
        h_name = host['Hostname']
        h_desc = host['Description']
        h_ip = host['IP Address']
        h_interfaces = []
        h_proxy = host['Proxy']
        h_tags = []

        if (host['Interfaces'] == 'DO_NOT_ADD'):
            print('Skipping host: {}'.format(h_name))
            continue

        # Check and skip existing hosts
        if args.s:
            f = {'host': h_name}
            hosts = zapi.host.get(
                filter=f, output='extend', selectTags='extend')
            if hosts:
                print('Host {} already exists!! Skpping'.format(h_name))
                continue

        print('Working on: {}'.format(h_name))

        # Build Tags object
        for tagString in host['Tags'].split(","):
            [tagName, tagValue] = tagString.split("=")
            h_tags.append({
                'tag': tagName,
                'value': tagValue
            })
        # jsonPrint(h_tags)

        # Build interface object
        for interface in host['Interfaces'].split("-"):
            if (interfaceType[interface] == 1):
                port = 10050
            else:
                port = 161

            h_interfaces.append({
                'type': interfaceType[interface],
                'main': 1,
                'useip': 1,
                'ip': h_ip,
                'dns': "",
                'port': port
            })

        # Build hostgroup object
        for hostgroup in host['Groups'].split("-"):
            h_groups.append({
                'groupid': hostGroupId[hostgroup],
            })

        # Build template object
        for template in host['Templates'].split("-"):
            h_templates.append({
                'templateid': templateId[template],
            })

        if len(h_proxy) > 0:
            zapi_result = zapi.host.create(host=h_name, tags=h_tags, description=h_desc, interfaces=h_interfaces,
                                           groups=h_groups, templates=h_templates, proxy_hostid=proxyId[h_proxy])

        else:

            zapi_result = zapi.host.create(
                host=h_name, tags=h_tags, description=h_desc, interfaces=h_interfaces, groups=h_groups, templates=h_templates)
        jsonPrint(zapi_result)


if __name__ == "__main__":
    main(sys.argv[1:])
