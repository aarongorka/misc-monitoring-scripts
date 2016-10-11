#!/usr/bin/env python
"""
Nagios 3 -> Nagios 4 migration script. Nagios 4 no longer requires that 
backslashes are escaped.
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
  if re.search("check_command.*check_file_", line) or re.search("check_command.*check_file2", line):
    lines[lineno] = re.sub(r"\\\\", r"\\", lines[lineno])
    lines[lineno] = re.sub(r"\\:", r":", lines[lineno])

out = open(options.filename, 'w')
out.writelines(lines)
out.close()

exit()
