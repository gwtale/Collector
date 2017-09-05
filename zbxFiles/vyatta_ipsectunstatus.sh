#!/bin/vbash

# TUN DOWN = 0
# TUN UP = 1
# TUN DISABLED = 2
# TUN MISSING = 3

PEER=$1
TUNNEL=$2

TUNSTATUS="$(/opt/vyatta/bin/vyatta-op-cmd-wrapper show vpn ipsec sa peer $PEER tunnel $TUNNEL |tail -n 3|head -n 1|awk '{ print $2 }')"
if [[ -z "$TUNSTATUS" ]];
then
    #Tunnel is either missing or disabled
    if [ -d "/opt/vyatta/config/active/vpn/ipsec/site-to-site/peer/$PEER/tunnel/$TUNNEL/disable" ]
    then echo "2";
    else echo "3"; # Tunnel is not managed by ipsec sarvice but is not disabled
    fi
else
    if [ "$TUNSTATUS" == "up" ]; 
    then echo 1;  
    else echo 0; fi
fi

