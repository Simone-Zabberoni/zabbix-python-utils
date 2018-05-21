# zabbix-python-snips

Zabbix snippets and sample code for:

- json parsing/LLD/item prototyping
- massive host insert
- massive hostgroup moving
- massive host details and properties modification 
- data extraction: inventory query, current problems
- hosts query
- item data extraction (history and trend)
- misc automation stuff

**Caution** : sample scripts are mostly without error checking and they assume that you know what you are doing!


## Requirements

- python 2.7
- py-zabbix (`pip install py-zabbix`)
- requests (`pip install requests`)

## Details and informations


### jsonLLD.py and jsonGet.py

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


### hostBulkInsert.py

From a single csv file:
- create hostgroups
- create hosts and
    - assign the correct interface
    - assign them to their correct groups
    - link them to the correct templates


*File format*

The format of the file is: `Full_host_group_path; Hostname-Description; Ip_address; Templates; Interfaces;`

- Full hostgroup path is a '-' delimited list of nested hostgroups (Zabbix syntax: group/subgroup1/subgroup2)
- Templates is a '-' delimited list of existing templates to apply or a 'DO_NOT_ADD' string
- Interfaces could be agent, snmp or both (agent-SNMP)


Sample hosts.csv (*without headers*):

```
ITALY-ITALY/MILAN-ITALY/MILAN/Servers;SomeItalianServer-Primary Domain controller;192.168.1.1;DO_NOT_ADD;agent;
ITALY-ITALY/MILAN-ITALY/MILAN/Router;ITMIRT01-Milan Primary Internet Router;192.168.1.254;Template ICMP Ping;agent;
ITALY-ITALY/MILAN-ITALY/MILAN/Core;ITMISWCORE-Milan core switch;192.168.1.10;Template SNMP Switch-Template ICMP Ping;agent-SNMP;
ITALY-ITALY/BOLOGNA-ITALY/BOLOGNA/Core;ITBOSWCORE-Bologna core switch;192.168.2.10;Template SNMP Switch-Template ICMP Ping;agent-SNMP;
```

**TODO**
- parametric zabbix host and access
- parametric csv file
- template existance check and what to do if template does not exists
- error check for existing hosts and overwrite/do not touch parameter


### hostMover.py - move hosts to hostgroups

From a csv file:
- move hosts to a specific hostgroup list

Uses the same host.csv format of hostBulkInsert.py.


### Miscellaneous snips
    
[TBD]



