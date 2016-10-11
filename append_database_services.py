#!/usr/bin/env python
"""
NAME
      append_database_services.py - Append database services to Nagios host files
SYNOPSIS
      ./append_database_services.py
DESCRIPTION
      Recurses through a folder and appends 3 services (Memory Grants Pending,
      Target Server Memory and memory - available) to any file containing 
      check_mssql_health services. Accounts for multiple SQL Server instances on a single server.
"""
import sys, os, re
from optparse import OptionParser
from os import getenv

def getservices(template, host_name, contactgroup, servicegroup, domain, instances):
  "Get services to be added"
  services = '\n'
  if instances:
    for instance in instances: 
      instance_backslash = "!\\\\\\\\{}".format(instance)
      instance_desc = " {} -".format(instance)
      services += """define service {{
	use				{},srv-pnp
	host_name			{}
	service_description		db -{} Memory Grants Pending
	contact_groups			{}
	servicegroups			{}
	check_command			check_mssql_health!{}!sql --name "`cat /etc/nagios/database-queries/memory_grants_pending.sql`" --name2 'MemoryGrantsPending' --units 'grants' --warning '0' --critical '4'{}
	notifications_enabled		0
	}}""".format(template, host_name, instance_desc, contactgroup, servicegroup, domain, instance_backslash, instance_desc)
      services += '\n'
      services += '\n'
      services += """define service {{
	use				{},srv-pnp
	host_name			{}
	service_description		db -{} Target Server Memory
	contact_groups			{}
	servicegroups			{}
	check_command			check_mssql_health!{}!sql --name "`cat /etc/nagios/database-queries/target_server_memory.sql`" --name2 'TargetServerMemory' --units 'B' --warning '999999999999' --critical '9999999999999'{}
	notifications_enabled		0
	}}""".format(template, host_name, instance_desc, contactgroup, servicegroup, domain, instance_backslash, instance_desc)
      services += '\n'
      services += '\n'
  else:
    instance_backslash = ''
    instance_desc = ''
    services += """define service {{
	use				{},srv-pnp
	host_name			{}
	service_description		db - Memory Grants Pending
	contact_groups			{}
	servicegroups			{}
	check_command			check_mssql_health!{}!sql --name "`cat /etc/nagios/database-queries/memory_grants_pending.sql`" --name2 'MemoryGrantsPending' --units 'grants' --warning '0' --critical '4'
	notifications_enabled		0
	}}""".format(template, host_name, contactgroup, servicegroup, domain)
    services += '\n'
    services += '\n'
    services += """define service {{
	use				{},srv-pnp
	host_name			{}
	service_description		db - Target Server Memory
	contact_groups			{}
	servicegroups			{}
	check_command			check_mssql_health!{}!sql --name "`cat /etc/nagios/database-queries/target_server_memory.sql`" --name2 'TargetServerMemory' --units 'B' --warning '999999999999' --critical '9999999999999'
	notifications_enabled		0
	}}""".format(template, host_name, contactgroup, servicegroup, domain)
    services += '\n'
    services += '\n'
  services += """define service{{
	use				{},srv-pnp
	host_name			{}
	service_description		memory - available
	contact_groups			{}
	servicegroups			{}
	check_command			check_nrpe!CheckCounter -a "Counter=\Memory\Available Bytes" ShowAll MinWarn=157286400 MinCrit=104857600
	notifications_enabled		0
	}}""".format(template, host_name, contactgroup, servicegroup)
  services += '\n'
  services += '\n'
  return(services)

def getfiles():
  "Get files that need to be edited"
  requiredfiles = []
  objpath = os.getenv("HOME") + "/nagios-objects/hosts"
  for root, dirs, files in os.walk(objpath, topdown=False):
    for name in files:
      filename = os.path.join(root, name)
      if os.path.isfile(filename):
        fh = open(filename, 'r')
        lines = fh.readlines()
        fh.close()
        for lineno,line in enumerate(lines):
          if re.search(r"check_mssql_health", line) and not filename in requiredfiles:
            requiredfiles.append(filename)
  return(requiredfiles)

def addservices(file):
  "Add services to host"
  template = ''
  host_name = ''
  contactgroup = ''
  servicegroup = ''
  domain = ''
  instances = []
  fh = open(file, 'r')
  lines = fh.readlines()
  fh.close()
  for lineno,line in enumerate(lines):
    if re.search(r'contact_group', line) and not contactgroup:
      try:
        contactgroup = re.search(r'(cg_dba_mssql\w*)', line).group(1)
      except:
        continue
    elif re.search(r'check_command.*check_mssql_health.*', line) and not domain:
      try:
        domain = re.search(r'check_mssql_health\!([a-zA-Z\.]*)', line).group(1)
      except:
        continue
    elif re.search(r'use\s*', line) and not template:
      try:
        template = re.search(r'(db-mssql-[a-zA-Z0-9\-]*),', line).group(1)
      except:
        continue
    elif re.search(r'servicegroups', line) and not servicegroup:
      try:
        servicegroup = re.search(r'(sg_dba_mssql\w*)', line).group(1)
      except:
        continue
    elif re.search(r'check_command.*check_mssql_health.*\\\\\\\\', line):
      try:
        instance = re.search(r'\!\\\\\\\\(.*)$', line).group(1)
        instances.append(instance)
      except:
        continue
    elif re.search(r'host_name\s*', line) and not host_name:
      try:
        host_name = re.search(r'host_name\s*(.*)', line).group(1)
      except:
        continue
  instances = list(sorted(set(instances))) # sort and uniq
  if not template:
    template = 'generic-service'

  if not template or not host_name or not contactgroup or not servicegroup or not domain:
    print 'error'

  lines += getservices(template, host_name, contactgroup, servicegroup, domain, instances)

  out = open(file, 'w')
  out.writelines(lines)
  out.close()
  print "{:<30} {:<15} {:<30} {:<30} {:<15} {}".format(template, host_name, contactgroup, servicegroup, domain, instances)
        
def main():
  for file in getfiles():
    addservices(file)

if __name__ == '__main__':
  main()
