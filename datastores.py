#!/usr/bin/env python
"""
NAME
    datastores.py - Create Nagios host configuration file to monitor all
    datastores visible in a vCenter instance.
SYNOPSIS
    ./datastores.py --username USERNAME [--password PASSWORD] --template FILE
    --vcenter HOSTNAME --outfile FILE
DESCRIPTION
    Connects to a vCenter instance with the credentials specified, enumerates
    all available datastores (and the hosts they're connected to) and creates a
    Nagios configuration file to monitor the performance and space free for
    each datastores.
"""
import sys, os, re
import logging
from os import getenv
import socket
from optparse import OptionParser
import getpass
import atexit
from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
import requests # for disabling SSL error messages

def get_template_lines(template_filename):
    "Open template file and read in lines"
    fh = open(template_filename, 'r')
    template_lines = fh.readlines()
    logging.debug("var template_lines length is {}".format(len(template_lines)))
    if len(template_lines) < 5:
      logging.critical("Template file seems abnormally small ({} lines), which may indicate something went wrong with the script.".format(len(template)))
      exit(1)
    fh.close()
    logging.debug("Template is {} lines long.".format(len(template_lines)))
    return(template_lines)

def get_host_name(template_lines):
    "Get 'host_name' directive from a string"
    for line in template_lines:
      try:
        host_name = re.search(r"host_name\s+(.*)", line).group(1)
      except:
        continue
    logging.debug("host_name: {}".format(host_name))
    return(host_name)


def get_host_address(template_lines):
    "Get 'address' directive from a string"
    for line in template_lines:
      try:
        host_address = re.search(r"address\s+(.*)", line).group(1)
      except:
        continue
    logging.debug("host_address: {}".format(host_address))
    return(host_address)

def get_esxi_hosts(hostname, username, password):
    "Gets a list of ESXi hosts by connecting to vCenter"
    service_instance = connect.SmartConnect(host=hostname,user=username,pwd=password,port=443)
    if not service_instance:
         print("Could not connect to the specified host using specified "
               "username and password")
         exit(1)
    atexit.register(connect.Disconnect, service_instance)
    content = service_instance.RetrieveContent()
    
    objview = content.viewManager.CreateContainerView(content.rootFolder,[vim.HostSystem],True)
    esxi_hosts = objview.view
    objview.Destroy()
    logging.info("ESXi hosts: {}".format([esxi_host.name for esxi_host in esxi_hosts]))
    esxi_hosts.sort(key=lambda x: x.name, reverse=True)
    logging.info("The number of ESXi hosts is {}".format(len(esxi_hosts)))
    if len(esxi_hosts) < 50:
      logging.critical("Number of ESXi hosts found ({}) is abnormally low, which may indicate something went wrong with the script.".format(len(esxi_hosts)))
      exit(1)
    return(esxi_hosts)

def get_services(esxi_hosts, host_name, vcenter_fqdn):
    "Returns a list of services to monitor datstores for a list of given ESXi hosts"
    services = ""
    datastores_seen = []
    mounts_debug = []
    for esxi_host in esxi_hosts:
        mounts = esxi_host.configManager.storageSystem.fileSystemVolumeInfo.mountInfo
        mounts.sort(key=lambda x: x.volume.name, reverse=True)
        mounts_debug += mounts
        logging.debug("Number of mounts on {} is {}".format(esxi_host.name, len(mounts)))
        for mount in mounts:
            if mount.volume.type == "VMFS" and mount.mountInfo.accessible == True and not mount.volume.name in datastores_seen and not re.search("\(|\)", mount.volume.name):
                datastores_seen.append(mount.volume.name)
                services += """
define service{{
\tuse\t\t\t\tvmware-service-datastore-usage,srv-pnp
\thost_name\t\t\t{}
\tcontact_groups\t\t\tcg_infra_vmware
\tservicegroups\t\t\tsg_infra_vmware
\tservice_description\t\tDS - Usage - {}
\tcheck_command\t\t\tbox293_check_vmware!{}!Datastore_Usage!--host!{}!--name!{}!!
\t}}
""".format(host_name, mount.volume.name, vcenter_fqdn, esxi_host.name, socket.getfqdn(mount.volume.name))

                services += """
define servicedependency{{
\tdependent_host_name\t\t{}
\tdependent_service_description\tDS - Usage - {}
\thost_name\t\t\t{}
\tservice_description\t\tGuest status
\texecution_failure_criteria\tn
\tnotification_failure_criteria\tw,c,u
\t}}
""".format(host_name, mount.volume.name, host_name)

                services += """
define service{{
\tuse\t\t\t\tvmware-service-datastore-perf,srv-pnp
\thost_name\t\t\t{}
\tcontact_groups\t\t\tcg_infra_vmware
\tservicegroups\t\t\tsg_infra_vmware
\tservice_description\t\tDS - Perf - {}
\tcheck_command\t\t\tbox293_check_vmware!{}!Datastore_Performance!--host!{}!--name!{}!!
\t}}
""".format(host_name, mount.volume.name, vcenter_fqdn, esxi_host.name, socket.getfqdn(mount.volume.name))

                services += """
define servicedependency{{
\tdependent_host_name\t\t{}
\tdependent_service_description\tDS - Perf - {}
\thost_name\t\t\t{}
\tservice_description\t\tGuest status
\texecution_failure_criteria\tn
\tnotification_failure_criteria\tw,c,u
\t}}

""".format(host_name, mount.volume.name, host_name)
    # Convert to a list of lines to match template input
    try:
        # Assume you get multiline text
        services = services.splitlines()
        services = [x + '\n' for x in services]
    except AttributeError:
        pass
    mounts_debug2 = []
    mounts_debug2 += list(sorted(set([mount.volume.name for mount in mounts_debug])))
    logging.info("Number of mount points: {}".format(len(mounts_debug2)))
    logging.info("Mount points: {}".format(mounts_debug2))
    return(services)

def main():
    requests.packages.urllib3.disable_warnings() # disable SSL errors on vCenter
    
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    parser = OptionParser()
    parser.add_option("--username", metavar="USERNAME", dest="username", help="username used to connect to vCenter")
    parser.add_option("--password", metavar="PASSWORD", dest="password", help="password used to connect to vCenter. Will prompt if not specified")
    parser.add_option("--template", metavar="FILE", dest="template_filename", help="template that will be appended to in order to generate the Nagios cfg file")
    parser.add_option("--vcenter", metavar="HOSTNAME", dest="vcenter", help="vCenter host used in the '--server' argument of box293_check_vmware")
    parser.add_option("--outfile", metavar="FILE", dest="outfile", help="File to write the generated configuration to")
    (options, args) = parser.parse_args()

    if options.password:
      password = options.password
    else:
      try:
        password = getpass.getpass()
      except:
        logging.warning("Need a password.")
        exit(1)
    template_lines = get_template_lines(options.template_filename)
    host_name = get_host_name(template_lines)
    host_address = get_host_address(template_lines)
    esxi_hosts = get_esxi_hosts(host_address, options.username, password)
    services = get_services(esxi_hosts, host_name, options.vcenter)
    output = template_lines + services
    logging.info("The number of lines in the generated configuration file is {}".format(len(output)))
    if len(output) < 4000:
      logging.critical("Total number of lines ({}) in the generated configuration file is abnormally low. This may indicate something went wrong with the script.".format(len(output)))
      exit(1)
    out = open(options.outfile, 'w')
    out.writelines(output)
    out.close()

if __name__ == '__main__':
    main()
