#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sample JSON LLD script

Mockup json from: https://jsonplaceholder.typicode.com/users
Produces JSON for Zabbix LLD according to https://www.zabbix.com/documentation/3.4/manual/discovery/low_level_discovery


Install needed libraries:
        pip install requests

"""


import requests
import json

jsonSource = "https://jsonplaceholder.typicode.com/users"
lld = {}
data = []
lld['data'] = data

session = requests.Session()
response = session.get(jsonSource)

for jsonObject in response.json():
    data.append ( {
        '{#NAME}':  jsonObject['name'],
        '{#ID}':  jsonObject['id'],
        '{#URL}':  jsonSource + '/' + str(jsonObject['id'])
    } )

print json.dumps(lld)
