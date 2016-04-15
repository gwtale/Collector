import string
import modules.SLApi.vyatta as vyatta

import modules.log.syslog as syslog

logger = syslog.getLogger(__name__)

"""    
#vpnStatusTxt = vyatta.getVyattaInfo("10.150.135.45", "vyatta", "W3MvlmtX", "show vpn ipsec sa")
vpnStatusTxt = open('data/testeVyatta.txt', 'r').read()
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
"""
vrrpTxt = vyatta.getVyattaInfo("10.150.135.45", "vyatta", "W3MvlmtX", "show vrrp")
print vyatta.parseUpDown(vrrpTxt)