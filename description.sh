#!/usr/bin/env bash
#- description.sh

## Updates a Nagios host to contain a display_name directive comprising of the host_name and alias

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
    -f | --filename) shift; FILENAME_OPT="$1";;
    -D | --debug )  DEBUG=1;;
    -h | --help)    echo "$help"; exit 3;;
    -v | --version) echo "$version"; exit 3;;
    -* | --* )      echo "Invalid option: $1" >&2; HELP=1;;
  esac
  shift
done

# main
content="$(cat "${FILENAME_OPT}")"
hostname="$(echo "${content}" | sed -nre 's/^\s+host_name\s+(.*)$/\1/p' | head -n 1)"
alias="$(echo "${content}" | sed -nre 's/^\s+alias\s+(.*)$/\1/p' | head -n 1)"
num="$(echo "${content}" | grep -nP '^\s+address\s+' | grep -Po '^[0-9]+')"
# http://stackoverflow.com/questions/5190966/using-sed-to-insert-tabs/5191165#5191165
sed -i "${num}i\\\tdisplay_name\t\t${hostname} - ${alias}" "${FILENAME_OPT}"
