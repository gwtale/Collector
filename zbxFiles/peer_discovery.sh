#!/bin/vbash
peers=`/opt/vyatta/bin/vyatta-op-cmd-wrapper show vpn ipsec sa detail |grep 'Peer IP'|awk '{print $3}'`
first=1
echo "{"
echo "\"data\":["
for peer in $peers
do
    tunnels=`/opt/vyatta/bin/vyatta-op-cmd-wrapper show vpn ipsec sa peer $peer |head -n -2| grep '  up\|  down'|awk '{print $1}'`
    for tunnel in $tunnels
    do
      if [[ $first = 0 ]] ; then echo "," ; fi
      first=0
      echo "    {\"{#VPN_PEER}\":\"$peer\",\"{#VPN_TUNNEL}\":\"$tunnel\"}"
    done
done
echo "]"
echo "}"
