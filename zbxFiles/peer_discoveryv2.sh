#!/bin/vbash
peers=`/opt/vyatta/bin/vyatta-op-cmd-wrapper show configuration commands|grep -E 'peer.*local-address'|awk '{print $6}'`
IFS=$'\r\n' GLOBIGNORE='*' command eval  'VPN=($(/opt/vyatta/bin/vyatta-op-cmd-wrapper show configuration commands|grep -E "site-to-site.*prefix"|grep -v allow))'

first=1
echo "{"
echo "\"data\":["
for peer in $peers
do
    # Create array of tunnels 
    tunnels=()
    for i in "${VPN[@]}"
    do
      if [[ $i == *$peer* ]]
      then
          tunnels+=("$(echo $i |awk '{print $8}')")
      fi
    done
    # Remove duplicates (tunnels array contains 2 lines per tunnel, remote and local prefix)
    tunnels2=$(echo "${tunnels[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' ')
    for a in ${tunnels2[@]}
    do
        if [[ $first = 0 ]] ; then echo "," ; fi
        first=0
        echo "    {\"{#VPN_PEER}\":\"$peer\",\"{#VPN_TUNNEL}\":\"$a\"}"
    done
done
echo "]"
echo "}"
