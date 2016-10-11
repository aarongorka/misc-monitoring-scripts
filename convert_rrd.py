#!/usr/bin/env python
# Converts a folder of rrd files from a pnp4nagios database to whisper files suitable for graphite-web and Graphios.
import sys, os, re
from optparse import OptionParser
from os import getenv
import fileinput
from pprint import pprint
from difflib import Differ
from lxml import etree
from subprocess import call
import shutil

parser = OptionParser()
parser.add_option("--hostname", metavar="HOST", dest="hostname")
parser.add_option("--rrdpath", metavar="PATH", dest="rrdpath")
(options, args) = parser.parse_args()

graphite_hostname = options.hostname
graphite_hostname = re.sub("\.", "_", graphite_hostname)
graphite_hostname = re.sub('/', "_",  graphite_hostname)
graphite_hostname = re.sub("'", "",  graphite_hostname)
graphite_hostname = re.sub('"', "",  graphite_hostname)
graphite_hostname = re.sub("'", "",  graphite_hostname)
graphite_hostname = re.sub('"', "",  graphite_hostname)
graphite_hostname = re.sub('\s', "_",  graphite_hostname)

path = '/var/lib/carbon'
rrdpath = options.rrdpath + options.hostname
wsppath = path + '/whisper/nagios/' + graphite_hostname

for root, dirs, files in os.walk(rrdpath, topdown=False):
  for name in files:
    if re.search("\.rrd", name, flags=re.IGNORECASE) and not os.path.isfile(rrdpath + '*.wsp'):
      call(["rrd2whisper", os.path.join(root, name)])

def getSeries(index, metric):
  print "index: " + index
  try:
    handler = open(rrdpath + '/' + metric + '.xml').read()
  except:
    print "No handler"
  try:
    root = etree.fromstring(handler)
  except:
    print "No root"
  for element in root.xpath("/NAGIOS/DATASOURCE"):
  #  print "element.text: " + element.text
    if element.find("DS").text == index:
      for i in element.iter("NAME"):
  #      print "i.text: " + i.text
        return i.text

# For the hostname provided, list the .wsp files we've just created
for root, dirs, files in os.walk(rrdpath, topdown=False):
  for name in files:
    if re.search("[0-9]+.wsp", name, flags=re.IGNORECASE):
      metric = re.sub("_[0-9]+\.wsp", "", name)
      graphite_metric = metric
      graphite_metric = re.sub(r"\.", "_", graphite_metric)
      graphite_metric = re.sub(r"\s", "",  graphite_metric)
      graphite_metric = re.sub(r"\)", "_", graphite_metric)
      graphite_metric = re.sub(r"\(", "_", graphite_metric)
      graphite_metric = re.sub(r"\\", "_", graphite_metric)
      graphite_metric = re.sub(r"\.", "_", graphite_metric)
      graphite_metric = re.sub(r",",  "_", graphite_metric)
      graphite_metric = re.sub(r"\/", "_", graphite_metric)
      graphite_metric = re.sub(r"\[", "_", graphite_metric)
      graphite_metric = re.sub(r"\]", "_", graphite_metric)
      graphite_metric = re.sub(r"\|", "_", graphite_metric)
      index = re.search("([0-9]+(?=.wsp))", name).group(1)
      graphite_series = getSeries(index, metric)
      try:
        graphite_series = re.sub(r"\s", "",  graphite_series)
        graphite_series = re.sub(r"\)", "_", graphite_series)
        graphite_series = re.sub(r"\(", "_", graphite_series)
        graphite_series = re.sub(r"\\", "_", graphite_series)
        graphite_series = re.sub(r"\.", "_", graphite_series)
        graphite_series = re.sub(r",",  "_", graphite_series)
        graphite_series = re.sub(r"\/", "_", graphite_series)
        graphite_series = re.sub(r"\[", "_", graphite_series)
        graphite_series = re.sub(r"\]", "_", graphite_series)
        graphite_series = re.sub(r"\|", "_", graphite_series)
        oldpath = os.path.join(root, name)
        call(["mkdir", "-p", wsppath]) # Just in case the host folder doesn't exist yet
        if re.search(r"HOST", graphite_metric): # can be _HOST_ or HOST
            newpath = wsppath + '/' + graphite_series  + '.wsp'
        else:
            call(["mkdir", "-p", wsppath + '/' + graphite_metric]) # Don't make folder if metric is HOST
            newpath = wsppath + '/' + graphite_metric + '/' + graphite_series  + '.wsp'
        if os.path.isfile(newpath):
            print "oldpath: " + oldpath
            print "newpath: " + newpath
            call(["whisper-merge", oldpath, newpath]) # If there's something already there, merge in to it
            os.remove(oldpath) # Remove old .wsp
        else:
            shutil.move(oldpath, newpath) # Else create it by moving it there
      except:
        print "No series found!"
#call(["chown", "-R", "carbon:carbon", newpath])
#call(["chcon", "-R", "-u", "system_u", "-r", "object_r", "-t", "var_lib_t", newpath])
#shutil.rmtree(rrdpath) 
