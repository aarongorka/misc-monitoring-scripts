#!/usr/bin/env python
"""
Updates all BizTalk thresholds in a given Nagios configuration file
"""
import sys, os, re
from optparse import OptionParser
from os import getenv
import fileinput
from pprint import pprint
from difflib import Differ

parser = OptionParser()
parser.add_option("--filename", metavar="FILE", dest="filename")
(options, args) = parser.parse_args()

fh = open(options.filename, 'r')
# Read lines
lines = fh.readlines()
# For lines get line number and line text
for lineno,line in enumerate(lines):
  if re.search("check_command.*database-queries.*BizTalk.*Receive", line):
    lines[lineno] = re.sub(r"--warning=[0-9]*", r"--warning=0", lines[lineno])
    lines[lineno] = re.sub(r"--critical=[0-9]*", r"--critical=100", lines[lineno])
  elif re.search("check_command.*database-queries.*BizTalk.*Suspended", line):
    lines[lineno] = re.sub(r"--warning=[0-9]*", r"--warning=0", lines[lineno])
    lines[lineno] = re.sub(r"--critical=[0-9]*", r"--critical=1000", lines[lineno])

out = open(options.filename, 'w')
out.writelines(lines)
out.close()

exit()
