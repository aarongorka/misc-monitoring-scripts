#!/usr/bin/env bash
#- XX_FILENAME

## Usage: XX_USAGE
## 
## XX_DESCRIPTION
##
##       -D|--debug    Print debug info
##       -h|--help     Show help options.
##       -v|--version  Print version info.
##
## Example
## XX_EXAMPLE

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
    -s | --someopt) shift; SOME_OPT="$1";;
    -D | --debug )  DEBUG=1;;
    -h | --help)    echo "$help"; exit 3;;
    -v | --version) echo "$version"; exit 3;;
    -* | --* )      echo "Invalid option: $1" >&2; HELP=1;;
  esac
  shift
done

# main
