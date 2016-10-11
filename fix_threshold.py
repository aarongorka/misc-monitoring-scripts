#!/usr/bin/python
"""
Update latches-wait-time threshold
"""
import sys, os, re
from optparse import OptionParser
from os import getenv
import fileinput

parser = OptionParser()
parser.add_option("--somefile", metavar="FILE", dest="somefile")
(options, args) = parser.parse_args()

regexpattern = re.compile('.*check_command.*latches-wait-time.*')

# Open file
fh = open(options.somefile, 'r')
# Read lines
lines = fh.readlines()
# For lines get line number and line text
for lineno,line in enumerate(lines):
# If regex match, do regex search and replace
# Add results to lines array
    if regexpattern.match(line):
        lines[lineno] = re.sub(r"--warning (?:[0-9]|\.)+ --critical (?:[0-9]|\.)+", "--warning 10000 --critical 20000", line)

out = open(options.somefile, 'w')
out.writelines(lines)
out.close()
