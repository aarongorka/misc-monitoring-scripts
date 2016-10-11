#!/usr/bin/python
"""
Consolidate sparse Nagios contactgroup files in to one file per app/team.
Ouputs to ~/tmp.
"""
import sys, os, re
import pynag
import pynag.Model
from pynag import Model

Model.cfg_file = os.getenv("HOME") + "/nagios.cfg"
pynag.Model.pynag_directory = os.getenv("HOME") + "/nagios-objects"

contactgroups = pynag.Model.Contactgroup.objects.all

apps = []

for contactgroup in contactgroups:
  contactgroup_name = contactgroup['contactgroup_name']
  contactgroup_name = re.sub('_email_only', '', contactgroup_name)
  contactgroup_name = re.sub('_lead',       '', contactgroup_name)
  contactgroup_name = re.sub('_mgr',        '', contactgroup_name)
  contactgroup_name = re.sub('_demo',       '', contactgroup_name)
  contactgroup_name = re.sub('_bus',        '', contactgroup_name)
  contactgroup_name = re.sub('_t[0-9]*',    '', contactgroup_name)
  apps.append(contactgroup_name)

apps = sorted(set(apps))

for app in apps:
  app_objs = pynag.Model.Contactgroup.objects.filter(contactgroup_name__contains=app)
  for app_obj in app_objs:
    app_obj.set_filename(os.getenv("HOME") + '/tmp/' + app + '.cfg')
    app_obj.save()
