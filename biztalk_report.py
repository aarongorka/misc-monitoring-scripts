#!/usr/bin/python
"""
Creates a .csv reporting on all thresholds for all BizTalk services
"""
import sys, os, re
from optparse import OptionParser
from os import getenv
import fileinput
import pynag
import pynag.Model
from pynag import Model
import csv


b = open('report.csv', 'w')
a = csv.writer(b)

Model.cfg_file = os.getenv("HOME") + '/nagios.cfg'

services = []
data = []
services = pynag.Model.Service.objects.filter(service_description__contains='BizTalk')

for service in services:
  if re.search(r'BizTalk - ', service['service_description']):
    try:
      warning = re.search(r'--warning=\'?([0-9]*)', service['check_command']).group(1)
      critical = re.search(r'--critical=\'?([0-9]*)', service['check_command']).group(1)
    except:
      warning = re.search(r'-w ([0-9]*)', service['check_command']).group(1)
      critical = re.search(r'-c ([0-9]*)', service['check_command']).group(1)
    data.append([service['host_name'], service['service_description'], str(warning), str(critical)])

data.insert(0, ['hostname', 'service description', 'warning', 'critical'])

a.writerows(data)
b.close()


exit ()
