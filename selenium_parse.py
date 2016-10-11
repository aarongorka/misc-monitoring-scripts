#!/usr/bin/python
"""
Creates a string to be used in the -b option of check_selenium_advanced using comments
Each comment creates a section that includes all commands until the next comment
Numbering is automatically added to order series in graphs
"""
import sys, os, re
from optparse import OptionParser
from os import getenv
import fileinput

parser = OptionParser()
parser.add_option("--file", metavar="FILE", dest="file")
(options, args) = parser.parse_args()


step_no = 0
cat_no = 0
cat_name = ''
output = ''

# Open file
fh = open(options.file, 'r')
# Read lines
lines = fh.readlines()
# For lines get line number and line text
for lineno,line in enumerate(lines):
# If regex match, do regex search and replace
# Add results to lines array
    if re.search('^#', line):
	if cat_no > 0:
            output += ':' + cat_name + '-'
        cat_no = cat_no + 1
        cat_name = line.lower()
        cat_name = cat_name.replace(' ', '_')
        cat_name = cat_name.replace('-', '_')
        cat_name = cat_name.replace('?', '')
        cat_name = cat_name.rstrip('\n')
        cat_name = cat_name.replace('#', "{0:0>2}".format(cat_no))
    if re.search('\$sel->', line):
        step_no = step_no + 1
	output += str(step_no) + ','

output += ':' + cat_name
output = output.replace(',:', ':')
output = output.rstrip(',')

#out = open(options.file, 'w')
#out.writelines(lines)
#out.close()
print output
