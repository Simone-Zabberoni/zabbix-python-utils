#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JSON Get script

Install needed libraries:
        pip install requests

Usage:
	$ jsonGet.py -i https://jsonplaceholder.typicode.com/users/10 -f name
	Clementina DuBuque

	$ jsonGet.py -i https://jsonplaceholder.typicode.com/users/10 -f company.name
        Hoeger LLC

	$ jsonGet.py -i https://jsonplaceholder.typicode.com/users -f 9.company.name
        Hoeger LLC

	$ jsonGet.py -i https://jsonplaceholder.typicode.com/users/9 -f address.geo
	{
	    "lat": "-38.2386",
	    "lng": "57.2232"
	}



TODOs:
- update documentation and usage

"""


import requests
import json
import sys, argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', required=True, metavar='Input URL')
parser.add_argument('-f', required=True, metavar='Dottet path to JSON Field')
parser.add_argument('-u', required=False, metavar='Username')
parser.add_argument('-p', required=False, metavar='Password')
args = parser.parse_args()

# Connect, with optional username and password
session = requests.Session()
response = session.get(args.i, auth=(args.u, args.p))

# Traverse json path
output = response.json()
for item in args.f.split('.'):
    if item.isdigit():
        # index - traverse lists
        try:
            output = output[int(item)]
        except:
            output = None
    else:
        # key - traverse dicts
        try:
            output = output.get(item)
        except:
            output = None

# Simple output for properties, pretty json output for dicts
if isinstance(output, dict):
    print ( json.dumps(output, indent=4, separators=(',', ': ')) )
else:
    print ( output )
