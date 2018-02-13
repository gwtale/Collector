#!/usr/bin/python

import xml.etree.ElementTree as et
import sys
import requests
import json
import os.path
#import modules.log.syslog as syslog
import xml.dom.minidom
import urllib3
import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#logger = syslog.getLogger(__name__)

### VARS ###
VROPSIP = sys.argv[1]
VROPSID = sys.argv[2]
VROPSPW = sys.argv[3]
ALERTID = sys.argv[4]
# Valid values for INFO
#     'status'
#     'startTime'
#     'alertLevel'
INFO = sys.argv[5]

ns = {'ops': 'http://webservice.vmware.com/vRealizeOpsMgr/1.0/'}

def getResponse(server, opt=None, userId=None, userPw=None):
    session = requests.Session()
    session.auth = (userId, userPw)
    auth = session.post("https://" + server, verify=False)
    response = session.get("https://" + server + "/" + opt, verify=False)
    return response.content


rawResponse = getResponse(VROPSIP, "/suite-api/api/alerts/"+ALERTID, VROPSID, VROPSPW)
xmlResponse = xml.dom.minidom.parseString(rawResponse)
_tree = et.fromstring(rawResponse)
for child in _tree:
    if INFO in child.tag:
        if INFO == 'startTime':
            startTimeStr = datetime.datetime.fromtimestamp(int(child.text) / 1000).strftime('%Y-%m-%d %H:%M:%S')
            print(startTimeStr)
        else:
            print(child.text)

