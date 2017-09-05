#!/bin/vbash
tunnels=`/opt/vyatta/bin/vyatta-op-cmd-wrapper show interfaces tunnel|grep 'tun'|awk '{print $1}'`
first=1
echo "{"
echo "\"data\":["
for tunnel in $tunnels
do
      if [[ $first = 0 ]] ; then echo "," ; fi
      first=0
      peer=`/opt/vyatta/bin/vyatta-op-cmd-wrapper show interfaces tunnel $tunnel |grep peer|awk '{ print $4 }'`
      echo "    {\"{#TUN_INT}\":\"$tunnel\",\"{#GRE_PEER}\":\"$peer\"}"
done
echo "]"
echo "}"
