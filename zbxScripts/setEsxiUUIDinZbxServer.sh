server=$1
fqdn=$2
user=$3
passwd=$4
zbxsvrip=$5
zbxsvrid=$6
zbxsvrpw=$7
 
rm ~/.ssh/known_hosts
cd /var/Collector/zbxScripts
if ping -c1 $server &>/dev/null; then
    echo 'Host is alive...'
    echo 'Enabling MOB for '$fqdn'...'
    esxcfg-advcfg --server $server --username $user --password $passwd --set true Config.HostAgent.plugins.solo.enableMob
    cat <<EOF | python -
#!/usr/bin/python
from pyzabbix import ZabbixAPI
import urllib2,ssl,base64,re
zapi = ZabbixAPI(url='http://$zbxsvrip/zabbix/', user='$zbxsvrid', password='$zbxsvrpw')
url = 'https://$server/mob/?moid=ha-host&doPath=hardware.systemInfo'
hostid = ''
def getUUID():
    request = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % ('$user', '$passwd')).replace('\n', '')
    request.add_header('Authorization', 'Basic %s' % base64string)
    gcontext = ssl._create_unverified_context()
    result = urllib2.urlopen(request, context=gcontext)
    page_content = result.read()
    result = re.search('<uuid>(.*)</uuid>', page_content)
    print('VM UUID = ' + result.group(1))
    return result.group(1)

def updateHost(hostid,uuid):
    result = zapi.do_request('host.update', {
        'hostid': hostid,
        'host': uuid,
        'name': '$fqdn'
    })
    print(result)

def getHostId():
    result = zapi.do_request('host.get', {
        'output': 'extend',
        'filter': {
            'name': ['$fqdn']
        }
    })
    print('Found host with ID#' + str(result['result'][0]['hostid']))
    return result['result'][0]['hostid']
uuid = getUUID()
hostid = getHostId()
updateHost(hostid,uuid)
EOF
    # -------------------------------------------------------------------
    echo 'UUID configured. Disabling MOB...'
    esxcfg-advcfg --server $server --username $user --password $passwd --set false Config.HostAgent.plugins.solo.enableMob
    echo 'Done.'
else
    echo 'Host unreachable. Skipping...'
fi
