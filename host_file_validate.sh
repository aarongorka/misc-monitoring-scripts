#!/usr/bin/env bash
#- host_file_validate.sh v0.1

## Checks for any Nagios host files that have services belonging to a different host

# Failsafe settings
LC_ALL=C
PATH='/sbin:/usr/sbin:/bin:/usr/bin'
#set -o noclobber
#set -o errexit
#set -o nounset
#set -o pipefail
#shopt -s nullglob
unalias -a

# --help and --version functions
help=$(grep "^## " "${BASH_SOURCE[0]}" | cut -c 4-)
version=$(grep "^#- "  "${BASH_SOURCE[0]}" | cut -c 4-)

# getopts
while [[ -n "${1:-}" ]]; do
  case "$1" in
    -s | --someopt) shift; SOME_OPT="$1";;
    -D | --debug )  DEBUG=1;;
    -h | --help)    echo "$help"; exit 3;;
    -v | --version) echo "$version"; exit 3;;
    -* | --* )      echo "Invalid option: $1" >&2; HELP=1;;
  esac
  shift
done

# main
IFS=$'\n'
for i in $(find ${HOME}/Documents/repos/nagios-objects/hosts -name "*.cfg"); do 
  hostname_filename="$(echo -n "$i" | sed 's/\.cfg$//g' | sed 's/.*\///g')"
  noncompliant="${noncompliant} $(grep -nP '^\s+host_name\s+' "$i" | grep -ivP "${hostname_filename}")"
  if [[ -z ${noncompliant} ]]; then
    echo "$i: OK"
  fi
done
unset IFS
