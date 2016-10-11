#!/usr/bin/env bash
## Update NSClient++ configuration in preparation for new version. WIP.

help=$(grep "^## " "${BASH_SOURCE[0]}" | cut -c 4-)
version=$(grep "^#- "  "${BASH_SOURCE[0]}" | cut -c 4-)

while [[ -n "${1:-}" ]]; do
  case "$1" in
    -f | --file) shift;  FILE="$1";;
    -D | --debug )           DEBUG=1;;
    -* | --* ) echo "Invalid option: $1" >&2; HELP=1;;
  esac
  shift
done

# Failsafe settings
PATH='/sbin:/usr/sbin:/bin:/usr/bin'
set -o noclobber
set -o errexit
set -o nounset
set -o pipefail
shopt -s nullglob
unalias -a

# Main
sed -i 's/CheckCounterMax\!memory \- pages\/sec.*/check_nrpe!check_memory_pages_per_sec/g' "${FILE}"
#sed -i 's/pages\/sec/pages per sec/g' "${FILE}"
sed -i 's/CheckCounterMax\!Processor Q Length.*/check_nrpe!check_processor_queue_length/g' "${FILE}"
sed -i 's/check_service_state$/check_nrpe!check_service_state/g' "${FILE}"
sed -i 's/CheckCounterMin\!.*/check_nrpe!check_system_uptime/g' "${FILE}"

#cat ~/nagios-templates/new-stuff.cfg | tee -a "${FILE}"
