#!/bin/bash
IP=$1
ID=$2
PW=$3

rm ~/.ssh/known_hosts
cd /var/Collector/zbxScripts
if netstat -l|grep 8000 > /dev/null; then echo 0 > /dev/null; else echo "waiting for simpleHTTPserver" && exit; fi
if curl -s http://$IP:10050 > /dev/null; then echo "agent is listening"; else ./installZbxAgent.exp $IP $ID "$PW" && echo "installZbxAgent.exp executed"; fi
