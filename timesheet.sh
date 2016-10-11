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
#set -o errexit
set -o nounset
#set -o pipefail
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

# http://unix.stackexchange.com/questions/123979/how-to-extract-logs-between-two-time-stamps
convertToEpoch(){
    #converts to epoch time
    local _date=$1
    local epoch_date=`date --date="$_date" +%s`
    echo $epoch_date
}

#http://stackoverflow.com/questions/12199631/convert-seconds-to-hours-minutes-seconds
function show_time () {
    num=$1
    min=0
    hour=0
    day=0
    if((num>59));then
        ((sec=num%60))
        ((num=num/60))
        if((num>59));then
            ((min=num%60))
            ((num=num/60))
            if((num>23));then
                ((hour=num%24))
                ((day=num/24))
            else
                ((hour=num))
            fi
        else
            ((min=num))
        fi
    else
        ((sec=num))
    fi
    echo "$day"d "$hour"h "$min"m "$sec"s
}

# main
for i in monday tuesday wednesday thursday friday; do
  day="$(sudo journalctl -m | grep "^$(date -dlast-${i} | sed -r 's/^\w+ //g' | grep --color=none -Po '^\w+ [0-9]{2}')" )"
  last="$(echo "${day}" | tail -q -n 1 | grep -Po "^\w+ [0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}")"
  first="$(echo "${day}" | head -q -n 1 | grep -Po "^\w+ [0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}")"
#  echo "last: ${last}"
#  echo "first: ${first}"
  lastepoch="$(convertToEpoch "${last}")"
  firstepoch="$(convertToEpoch "${first}")"
#  echo "lastepoch: ${lastepoch}"
#  echo "firstepoch: ${firstepoch}"
  diff="$(expr ${lastepoch} - ${firstepoch})"
#  echo "diff: ${diff}"
  time="$(show_time "${diff}")"
  echo "${i}: ${time}"
done
