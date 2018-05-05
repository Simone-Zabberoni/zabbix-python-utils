# zabbix-python-snips

Zabbix snippets and sample code for:

- massive host insert
- massive hostgroup moving
- massive host details and properties modification 
- data extraction: inventory query, current problems
- misc automation stuff

**Caution** : sample scripts are mostly without error checking and they assume that you know what you are doing!


## Requirements

- python 2.7
- py-zabbix (`pip install py-zabbix`)


## Details and informations



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


[...]

    


