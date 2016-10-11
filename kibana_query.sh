#!/usr/bin/env bash
#- kibana_query.sh

## Creates a lucene query to only show notifications for a given Nagios contactgroup

# Failsafe settings
LC_ALL=C
PATH='/sbin:/usr/sbin:/bin:/usr/bin'
set -o noclobber
set -o errexit
set -o nounset
set -o pipefail
shopt -s nullglob
unalias -a

# --help and --version functions
help=$(grep "^## " "${BASH_SOURCE[0]}" | cut -c 4-)
version=$(grep "^#- "  "${BASH_SOURCE[0]}" | cut -c 4-)

# getopts
while [[ -n "${1:-}" ]]; do
  case "$1" in
    -a | --app) shift; app="$1";;
    -D | --debug )  DEBUG=1;;
    -h | --help)    echo "$help"; exit 3;;
    -v | --version) echo "$version"; exit 3;;
    -* | --* )      echo "Invalid option: $1" >&2; HELP=1;;
  esac
  shift
done

# main
OUTPUT="$(grep -Po --no-filename "(?<=members).*" ~/nagios-objects/contactgroups/${app}*.cfg | sed 's/\s*//g' | tr ',' '\n' | sort | uniq)"
echo "$OUTPUT"

echo -n "("

IFS=$'\n'
for i in ${OUTPUT}; do
  echo -n "nagios_notifyname:\"${i}\" OR "
done

echo -n ")"
