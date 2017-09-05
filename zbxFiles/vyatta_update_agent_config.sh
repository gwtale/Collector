#!/bin/vbash
wget -N ftp://208.43.238.157/pub/zabbix/userparameters/vyatta_userparams.conf -q -O /etc/zabbix/zabbix_agentd.d/vyatta_userparams.conf
wget -N ftp://208.43.238.157/pub/zabbix/scripts/peer_discovery.sh -q -O /etc/zabbix/peer_discovery.sh
wget -N ftp://208.43.238.157/pub/zabbix/scripts/gre_discovery.sh -q -O /etc/zabbix/gre_discovery.sh
chmod +x /etc/zabbix/peer_discovery.sh
chmod +x /etc/zabbix/gre_discovery.sh

# Add start zabbix agent into crontab
CRON="0 1 * * * /etc/init.d/zabbix-agent restart"
( crontab -l | grep -v "/etc/init.d/zabbix-agent restart" ; echo "$CRON" ) | crontab -

