# List Nagios  hosts that don't have an associated hostgroup
for HOST in $(find "${HOME}/nagios-objects/hosts" -type f -name "*.cfg" | sed 's/.*\///g' | sed 's/.cfg//g'); do 
	echo -n "$HOST " 
	cat ${HOME}/nagios-objects/hostgroups/*.cfg | grep -c "$HOST"
done | awk '{print $2 " " $1}' | sort -nr

