#!/usr/bin/python
import xml.etree.ElementTree as et
import sys
import datetime

### VARS ###
VROPSIP = sys.argv[1]
inputAlertid = sys.argv[2]
infoType = sys.argv[3]

sherlockDir = '/var/Collector/'
alertsFile = sherlockDir + 'data/vrops_alerts_' +  VROPSIP + '.xml'

ns = {'ops': 'http://webservice.vmware.com/vRealizeOpsMgr/1.0/'}
############
try:
    alertsTree = et.parse(alertsFile)
    alertsRoot = alertsTree.getroot()
except e:
    print("ERROR: " + e)
    sys.exit(2)

for alert in alertsRoot.findall('ops:alert', ns):
    alertID = alert.find('ops:alertId', ns)
    if alertID.text == inputAlertid:
        if infoType == "status":
            _status = alert.find('ops:status', ns)
            print(_status.text)
        elif infoType == "severity":
            _level = alert.find('ops:alertLevel', ns)
            print(_level.text)
        elif infoType == "startTime":
           _time = alert.find('ops:startTimeUTC', ns)
           startTimeStr = datetime.datetime.fromtimestamp(int(_time.text) / 1000).strftime('%Y-%m-%d %H:%M:%S')
           print(startTimeStr)
        else:
           print("Invalid option")
