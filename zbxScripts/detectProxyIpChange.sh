#!/bin/bash
IP=$1
ID=$2
PW=$3

FOUND=`grep "tun0" /proc/net/dev`

if  [ -n "$FOUND" ] ; then
    echo "tun0 found"
else
    echo "tun0 not present. skipping..."
    exit
fi

if [ ! -e /tmp/zbxProxyIp_$IP ]; then
    ifconfig tun0 | grep "inet addr:" | cut -d: -f2 | awk '{print $1}' > /tmp/zbxProxyIp_$IP
fi

OLDIP=`cat /tmp/zbxProxyIp_$IP`
NEWIP=`ifconfig tun0 | grep "inet addr:" | cut -d: -f2 | awk '{print $1}'`

if [ "$OLDIP" != "$NEWIP" ]; then
    cp /var/Collector/zbxScripts/updateProxyIP.exp /tmp/updateProxyIP_$IP.exp
    /tmp/updateProxyIP_$IP.exp $IP $ID $PW
    sleep 5
    ifconfig tun0 | grep "inet addr:" | cut -d: -f2 | awk '{print $1}' > /tmp/zbxProxyIp_$IP
    rm /tmp/updateProxyIP_$IP.exp
    echo "proxy IP updated"
else
    echo "no update needed"
fi
