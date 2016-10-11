#!/usr/bin/env python
"""
NAME
    db_list.py - Dynamically update list of databases to monitor for a Microsoft
    SQL Server instance or AlwaysOn Availability Group listener.
SYNOPSIS
    ./db_list.py --filename FILE 
DESCRIPTION
    Updates MS SQL Server services in a given Nagios configuration file. This
    is done by connecting to the instance/listener in question and running
    various SQL queries to pull database information. Credentials are pulled
    from the Nagios resource.cfg file.
"""
import sys, os, re
import logging
from optparse import OptionParser
from os import getenv
import fileinput
import pymssql
import socket

def is_ag(hostname):
  "Returns True if the server is in an Availability Group"
  cursor.execute("SELECT CONVERT(sysname, SERVERPROPERTY('IsHadrEnabled'))")
  partofag = cursor.fetchone()
  logging.debug("partofag: {}".format(partofag))
  if not re.search("None", str(partofag)): # Probably not the best way to do this
    is_ag = True
  else:
    is_ag = False
  logging.debug('Part of an AG? {}'.format(is_ag))
  return(is_ag)

def get_listeners(hostname):
  "Returns a list of listeners present for any AGs that the specified host is part of"
  listeners = []
  cursor.execute("SELECT dns_name FROM sys.availability_group_listeners")
  row = cursor.fetchone()
  while row:
      listeners += row
      row = cursor.fetchone()
  logging.info('List of listeners: {}'.format(listeners))
  return(listeners)

def is_listener(hostname):
  "Returns True if the given hostname is a listener, false if it's an instance"
  is_listener = False
  listeners = get_listeners(hostname)
  if shorthost.upper() in (listener.upper() for listener in listeners):
    return(True)
  else:
    return(False)

def get_all_databases(hostname):
  "Gets a list of all databases available on an AG or instance"
  databases = []
  cursor.execute("SELECT name FROM sys.databases")
  row = cursor.fetchone()
  while row:
      databases += row
      row = cursor.fetchone()
  logging.debug("List of all databases: {}".format(databases))
  return(databases)

def get_listener_databases(hostname):
  "Returns a list of database to be included on a given listener. This query was created in collaboration with mkoshy."
  koshy = []
  cursor.execute("""
SELECT
 (HRCS.database_name) as "DB name"
FROM
sys.availability_groups_cluster AS AGC
  INNER JOIN sys.dm_hadr_availability_replica_cluster_states AS RCS
   ON
    RCS.group_id = AGC.group_id
  INNER JOIN sys.dm_hadr_availability_replica_states AS ARS
   ON
    ARS.replica_id = RCS.replica_id
  INNER JOIN sys.availability_group_listeners AS AGL
   ON
    AGL.group_id = ARS.group_id
       INNER JOIN sys.dm_hadr_database_replica_cluster_states AS HRCS
       ON
       RCS.replica_id=HRCS.replica_id 
where 
ARS.role_desc='PRIMARY'
and AGL.dns_name=\'""" + hostname + "\'")
  row = cursor.fetchone()
  while row:
    koshy += row
    row = cursor.fetchone()
  logging.info('List of listener databases: {}'.format(koshy))
  return(koshy)

def get_instance_databases(hostname):
  "Returns a list of databases to add to excluded from a given instance."
  ag_databases = []
  # If it's an instance, we want to exclude any databases assigned to any listener
  cursor.execute("select database_name from sys.availability_databases_cluster where group_id in (select group_id from sys.availability_group_listeners)")
  row = cursor.fetchone()
  while row:
      ag_databases += row
      row = cursor.fetchone()
  logging.debug('List of Availability Group databases on this instance: {}'.format(ag_databases))
  return(ag_databases)

def get_already_excluded(line):
  "Gets a list of databases that are already being excluded in a command"
  alreadyexcluded_search = re.search("--name=(.*) --regexp", line) # Not all commands specify these arguments so we better check
  if alreadyexcluded_search:
    alreadyexcluded = alreadyexcluded_search.group(1)
    alreadyexcluded = alreadyexcluded.translate(None, r"\^(?!')\$") # Delete any of these characters to remove any regex from the string
    alreadyexcluded = alreadyexcluded.split('|')
    logging.debug("Some databases have already been excluded")
  else:
    logging.debug("There were no existing excluded databases")
    return(False)
  return(alreadyexcluded)

def update_command(line, databases, is_listener):
  "For any given database-free/backup-age/transactions command, update the list of DBs to monitor"
  if is_listener and databases:
    logging.debug("Truth test: {}".format(is_listener))
    databases = [x for x in databases if not re.search('replica', x, re.IGNORECASE)] # don't monitor any DBs with 'replica' in the name
    databases = list(sorted(set(databases))) # sort and uniq
    if not re.search(r"--name='.*' --regexp", line):
      line = line.rstrip()
      line = re.sub("$", " --name='^()$$' --regexp\n", line)
    line = re.sub("(?<=--name=)'.*' ", "'^(" + '|'.join(databases).strip('|') + ")$$' ", line) # Add all databases to be included
  else:
    alreadyexcluded = get_already_excluded(line)
    if alreadyexcluded:
      databases += get_already_excluded(line)
    else:
      line = re.sub("$", r" --name='^(?\!(XX_PLACEHOLDER)$$)' --regexp", line) # Just preparing the proceding regexes and making sure we don't leave an invalid config behind
    databases.insert(0, 'tempdb')
    databases.insert(0, 'Perfmon')
    databases.insert(0, r'.*replica.*')
    databases.insert(0, r'.*Replica.*')
    databases = list(sorted(set(databases))) # sort and uniq
    logging.debug("Full list of databases to be excluded: {}".format(databases))
    line = re.sub("(?<=--name=)'.*' ", "'^(?\!(" + '|'.join(databases).strip('|') + ")$$)' ", line) # Add all databases to be excluded
  return(line)

def update_file(filename):
  "Updates a file"
  logging.debug('Filename is {}'.format(filename))

  if not is_ag(shorthost):
    logging.critical("This server is not part of an AG. Nothing to do.")
    exit()

  if is_listener(shorthost):
    logging.info("Listener: True")
    databases = get_listener_databases(shorthost)
    if not databases:
      logging.warning("There are no databases to monitor on {}.".format(server))
  else:
    logging.info("Listener: False")
    databases = get_instance_databases(shorthost)

  fh = open(filename, 'r')
  lines = fh.readlines()
  for lineno,line in enumerate(lines):
    if re.search('.*check_command.*check_mssql_health.*(?:database-free|backup-age|transactions)', line):
      lines[lineno] = update_command(line, databases, is_listener(shorthost))
      logging.info('Edited line no. {}:\n{}\n{}'.format(str(lineno), line.rstrip(), lines[lineno].rstrip()))
  fh.close()

  logging.debug("Variable 'lines' has type {} and is {} lines long.".format(type(lines), len(lines)))
  
  out = open(filename, 'w')
  out.writelines(lines)
  out.close()


def main():
  logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
  
  parser = OptionParser()
  parser.add_option("--filename", metavar="FILE", dest="filename")
  (options, args) = parser.parse_args()
  filename = options.filename
  
  
  # Get FQDN
  fh = open(options.filename, 'r')
  lines = fh.readlines()
  for line in lines:
    try:
      server = re.search(r"address\s+(.*)", line).group(1)
    except:
      continue
  fh.close()
  
  logging.debug('Server name is {}'.format(server))
  # Get domain to use in authentication
  domain =    server.split('.', 1)[1]
  shorthost = server.split('.', 1)[0]
  logging.debug('Domain name is {}'.format(domain))
  logging.debug('Short hostname is {}'.format(shorthost))
  
  # init variables
  databases = []
  ag_databases = []
  listeners = []
  combined_list = []
  
  resources = []
  resources.append('/etc/nagios/private/resource.cfg')
  resources.append('/usr/local/nagios/etc/resource.cfg')
  
  # Get username & password from resource file
  for resource in resources:
    try:
      fh = open(resource, 'r')
    except:
      continue
    else:
      break
  lines = fh.readlines()
  for line in lines:
    usersearch =     re.search(r"\$USER5\$=(.*)", line)
    if usersearch:
      user = usersearch.group(1)
    passwordsearch = re.search(r"\$USER6\$=(.*)", line)
    if passwordsearch:
      password = passwordsearch.group(1)
  fh.close()
    
  pymssql.timeout = 2
  pymssql.login_timeout = 2
  try:
    conn = pymssql.connect(server, domain + '\\' + user, password, "tempdb")
    cursor = conn.cursor()
  except:
    logging.exception('Failed to connect to {}.'.format(server))
    exit(1)
  else:
    logging.debug('Connected.')
  
  update_file(filename)
