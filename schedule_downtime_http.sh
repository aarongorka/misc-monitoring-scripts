NAGIOSURL="https://${NAGIOS_SERVER}/nagios/cgi-bin/cmd.cgi"
COMMENT="Automation"
HOSTNAME="${NAGIOS_HOSTNAME}"
MINUTES="120"
curl --silent --show-error \
    --data cmd_typ=55 \
    --data cmd_mod=2 \
    --data host=${HOSTNAME} \
    --data-urlencode "com_data=${COMMENT}" \
    --data trigger=0 \
    --data "start_time=$(date "+%Y-%m-%d+%H%%3A%M%%3A%S")" \
    --data "end_time=$(date "+%Y-%m-%d+%H%%3A%M%%3A%S" -d "$MINUTES min")" \
    --data fixed=1 \
    --data hours=2 \
    --data minutes=0 \
    --data childoptions=0 \
    --data btnSubmit=Commit \
    "${NAGIOSURL}" -u "${HTTP_USERNAME}:${HTTP_PASSWORD}"
