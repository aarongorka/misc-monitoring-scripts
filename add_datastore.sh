#!/usr/bin/env bash
#- XX_FILENAME

## Usage: ./add_datastore.sh --datastore <DATASTORE> --vcenter <FQDN> --host <FQDN> --outfile <PATH>
## 
## Appends a datastore to a Nagios configuration file
##
##       -d|--datastore     Name of the datastore to monitor
##       -c|--vcenter       vCenter host to query
##       -h|--host          Host that datastore is attached to
##       -o|--outfile       Nagios configuration file to append to
##       -D|--debug    Print debug info
##       -h|--help     Show help options.
##       -v|--version  Print version info.

help=$(grep "^## " "${BASH_SOURCE[0]}" | cut -c 4-)
version=$(grep "^#- "  "${BASH_SOURCE[0]}" | cut -c 4-)

while [[ -n "${1:-}" ]]; do
  case "$1" in
    -d | --datastore) shift; DATASTORE="$1";;
    -c | --vcenter) shift; VCENTER="$1";;
    -H | --host) shift; DATASTORE_HOST="$1";;
    -o | --outfile) shift; OUTFILE="$1";;
    -D | --debug ) DEBUG=1;;
    -h | --help) echo "$help"; exit 3;;
    -v | --version) echo "$version"; exit 3;;
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
OUTPUT="
define service{
	use				vmware-service-datastore-perf,srv-pnp
	host_name			dc1prd275
	contact_groups			cg_infra_vmware
	servicegroups			sg_infra_vmware
	service_description		DS - Perf - ${DATASTORE}
	check_command			box293_check_vmware!${VCENTER}!Datastore_Performance!--host!${DATASTORE_HOST}!--name!${DATASTORE}!!
	}

define service{
	use				vmware-service-datastore-usage,srv-pnp
	host_name			dc1prd275
	contact_groups			cg_infra_vmware
	servicegroups			sg_infra_vmware
	service_description		DS - Usage - ${DATASTORE}
	check_command			box293_check_vmware!${VCENTER}!Datastore_Usage!--host!${DATASTORE_HOST}!--name!${DATASTORE}!!
	}"

echo "${OUTPUT}" | tee -a "${OUTFILE}"
