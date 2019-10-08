#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Print host and proxy dependancies:

# ./getHostProxy.py
HostId: 10084 - Host: sample-host | Proxy ID: 0 - Proxy: NOPROXY
HostId: 13981 - Host: another-one | Proxy ID: 10255 - Proxy: proxy01
HostId: 13982 - Host: second-test | Proxy ID: 10255 - Proxy: proxy01
HostId: 13983 - Host: the-lastone | Proxy ID: 10256 - Proxy: proxy02
"""

from zabbix.api import ZabbixAPI
import sys

zabbixServer = 'http://yourserver/zabbix/'
zabbixUser = 'someuser'
zabbixPass = 'somepass'

zapi = ZabbixAPI(url=zabbixServer, user=zabbixUser, password=zabbixPass)

proxyes = {}
proxyes['0'] = 'NOPROXY'


for proxy in zapi.proxy.get():
    proxyes[proxy['proxyid']] = proxy['host']


if (sys.argv[1:]):
    # Filter based on the cmdline argument
    f = {'host': sys.argv[1:]}
    hosts = zapi.host.get(filter=f, output=['hostids', 'host', 'proxy_hostid'])
else:
    hosts = zapi.host.get(output=['hostids', 'host', 'proxy_hostid'])

for host in hosts:
    prx = host['proxy_hostid']
    print "HostId: {} - Host: {} | Proxy ID: {} - Proxy: {}".format(host['hostid'], host['host'], host['proxy_hostid'], proxyes[prx])
