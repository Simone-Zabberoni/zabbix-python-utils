#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JSON LLD script

Produces JSON for Zabbix LLD according to https://www.zabbix.com/documentation/3.4/manual/discovery/low_level_discovery

Requires a base url and a set of macro:field mappings


Usage:

$ jsonLLD.py -i https://jsonplaceholder.typicode.com/users -m "{#ID}:id,{#COMPANY}:company.name,{#NAME}:name,{#MAIL}:email"
{
    "data": [
        {
            "{#COMPANY}": "Romaguera-Crona",
            "{#ID}": 1,
            "{#MAIL}": "Sincere@april.biz",
            "{#NAME}": "Leanne Graham"
        },
        {
            "{#COMPANY}": "Deckow-Crist",
            "{#ID}": 2,
            "{#MAIL}": "Shanna@melissa.tv",
            "{#NAME}": "Ervin Howell"
        },
[cut]


Install needed libraries:
        pip install requests

"""

def getField (data, path):
    for item in path.split('.'):
        if item.isdigit():
            # index - traverse lists
            try:
                data = data[int(item)]
            except:
                data = None
        else:
            # key - traverse dicts
            try:
                data = data.get(item)
            except:
                data = None
    return(data)


import requests
import json
import sys, argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', required=True, metavar='Input URL')
parser.add_argument('-m', required=True, metavar='Macro:item mapping (ie: "{#ID}:id,{#NAME}:name" )')
parser.add_argument('-u', required=False, metavar='Username')
parser.add_argument('-p', required=False, metavar='Password')
args = parser.parse_args()

# Initialize the lld output structure
lld = {}
data = []
lld['data'] = data

# Connect, with optional username and password
session = requests.Session()
response = session.get(args.i, auth=(args.u, args.p))

for jsonObject in response.json():
    currentData={}

    # Build current record with all the required mappings
    for mapping in args.m.split(','):
        (macro, field) = mapping.split(':')
        fieldValue = getField(jsonObject, field)
        currentData[macro] = fieldValue

    # Add current record
    data.append(currentData)

# pretty json output
print ( json.dumps(lld, indent=4, separators=(',', ': ')) )

