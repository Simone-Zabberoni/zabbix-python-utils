# zabbix-python-snips

Zabbix snippets and sample code for:

- massive host insert
- massive hostgroup moving
- massive host details and properties modification
- data extraction: inventory query, current problems
- hosts query
- item data extraction (history and trend)
- misc automation stuff
- json parsing/LLD/item prototyping

**Caution** : sample scripts are mostly without error checking and they assume that you know what you are doing!

## Requirements

- python 2.7/3 (in progress on dev branch)
- py-zabbix
- requests

## Details and informations

### Arguments and env-var - in progress

All scripts will share the base command line with ENV variables support, like

```
# export ZABBIX_SERVER='https://your_zabbix_host/zabbix/'
# export ZABBIX_PASSWORD='admin'
# export ZABBIX_USERNAME='secretPassword'
```

### hostBulkInsert.py

From a single csv file:

- create hostgroups
- create hosts and
  - assign the correct interface
  - assign them to their correct groups
  - link them to the correct templates
  - add tags and descriptions
  - optional proxy assignment

Usage:

```
# hostBulkInsert.py -Z http://yourserver/zabbix -u admin -p somePass -f "zabbixHosts.csv" -s
```

_File format_

Sample csv file:

```
Hostname; IP Address; Groups; Tags; Description; ICMP; SNMP community; Proxy; Templates; Interfaces
SomeHost;8.8.8.8;Group1-Group2-Routers;TagName=someValue;Device Description;snmpCommnity;ZabbixProxyName;Template Net Cisco IOS SNMPv2;agent-SNMP
SecondHost;8.8.8.8;Group3-Group2-SiteA;FirstTag=value,TagName=anotherValue;Device Description;snmpCommnity;;Template Net Cisco IOS SNMPv2;agent-SNMP
```

Fields:

- Full hostgroup path is a '-' delimited list of nested hostgroups (Zabbix syntax: group/subgroup1/subgroup2)
- Templates is a '-' delimited list of existing templates to apply or a 'DO_NOT_ADD' string
- Interfaces could be agent, snmp or both (agent-SNMP)
- Tags are separated by ',' in the format TagName=TagValue

**TODO**

- proxy existance check and what to do if template does not exists
- template existance check and what to do if template does not exists
- tags are mandatory, add check

### hostMover.py - move hosts to hostgroups

From a csv file:

- move hosts to a specific hostgroup list

Uses the same host.csv format of hostBulkInsert.py.

### Miscellaneous snips

[TBD]

### jsonLLD.py and jsonGet.py (obsoleted by Zabbix HTTP Item in 4.0)

**jsonLLD.py**: Script for JSON low level discovery, produces JSON for Zabbix LLD according to https://www.zabbix.com/documentation/3.4/manual/discovery/low_level_discovery

Requires a base url and a set of macro:JSONfield to remap original data to Zabbix format

**jsonGet.py**: Gather data from URL, using a dotted notation

#### Command line:

```
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
```

```
$ jsonGet.py -i https://jsonplaceholder.typicode.com/users/10 -f name
Clementina DuBuque

$ jsonGet.py -i https://jsonplaceholder.typicode.com/users/10 -f company.name
Hoeger LLC

$ jsonGet.py -i https://jsonplaceholder.typicode.com/users/10 -f address.geo
{
    "lat": "-38.2386",
    "lng": "57.2232"
}

$ jsonGet.py -i https://jsonplaceholder.typicode.com/users -f 9.company.name
Hoeger LLC

```

#### Zabbix implementation:

- Create a Discovery rule of "Zabbix agent" type and set it to run `system.run[/usr/bin/jsonLLD.py]` (mind the path!)
- create an item prototype for each json field you want to work on (ie: Item name: `{#NAME} company name`, Item key `system.run[/usr/bin/jsonGet.py -i {#BASEURL}/{#ID} -f company.name]` )
