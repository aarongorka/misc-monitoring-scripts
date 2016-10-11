#!/usr/bin/python
"""
For a given Nagios configuration file, updates any specified service to have
the specified notes_url value.
"""
import sys, os, re
from optparse import OptionParser
from os import getenv
import fileinput

parser = OptionParser()
parser.add_option("--file", metavar="FILE", dest="file")
parser.add_option("--url", metavar="URL", dest="url")
parser.add_option("--service", metavar="STRING", dest="service")
(options, args) = parser.parse_args()

content = '\tnotes_url\t\t\t' + options.url + '\n'
commandregex = re.compile('check_command.*' + options.service)

# Open file
fh = open(options.file, 'r')
# Read lines
lines = fh.readlines()
# For lines get line number and line text
for lineno,line in enumerate(lines):
    if re.search(commandregex, line) and not re.search('^\s#', line):
        lines.insert(lineno + 1, content)
    if re.search(commandregex, line) and re.search('^\s#', line):
        lines.insert(lineno + 1, '#' + content)

out = open(options.file, 'w')
out.writelines(lines)
out.close()
