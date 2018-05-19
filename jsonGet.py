#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sample JSON Get script

Mockup json from: https://jsonplaceholder.typicode.com/users

Install needed libraries:
        pip install requests

Usage:
        $ jsonGet.py  -i 10 -f name
        Clementina DuBuque

        $ jsonGet.py  -i 10 -f phone
        024-648-3804
"""

import requests
import json
import sys, argparse


parser = argparse.ArgumentParser()
parser.add_argument('-i', required=True, metavar='User ID')
parser.add_argument('-f', required=True, metavar='\"Requested JSON Field\"')
args = parser.parse_args()

jsonSource = "https://jsonplaceholder.typicode.com/users/" + args.i

# Create the session object, then connect to the login page
session = requests.Session()
response = session.get(jsonSource)

print (response.json()[args.f])
