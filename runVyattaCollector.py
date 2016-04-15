import string
import modules.SLApi.vyatta as vyatta

import modules.log.syslog as syslog

logger = syslog.getLogger(__name__)

    
vpnStatusTxt = vyatta.getVyattaInfo("ams3vya02.brf.com", "10.136.81.58", "vyatta", "HXlxmeA9", "show vpn ipsec sa")
#vpnStatusTxt = open('data/testeVyatta.txt', 'r').read()
vpnStatusTxt = string.split(vpnStatusTxt, '\n')
#for line in vpnStatus:
#    print line
vpnStatus =  vyatta.parseVPN(vpnStatusTxt)
for status in vpnStatus:
    print "Peer ID: "+status['PeerID']
    print "Local ID: "+status['LocalID']
    print "Description: "+status['Description']
    for tunnel in status['Tunnel']:
        print tunnel.keys()[0] + " " + tunnel[tunnel.keys()[0]]

#vrrpTxt = vyatta.getVyattaInfo("ams3vya02.brf.com", "10.136.81.58", "vyatta", "HXlxmeA9", "show vrrp")
#print vyatta.parseUpDown(vrrpTxt)