#!/usr/bin/python

import sys
import requests
import json
import os.path
import xml.dom.minidom
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


### VARS ###
VROPSIP = sys.argv[1]
VROPSID = sys.argv[2]
VROPSPW = sys.argv[3]

def getResponse(server, opt=None, userId=None, userPw=None):
    session = requests.Session()
    session.auth = (userId, userPw)
    auth = session.post("https://" + server, verify=False)
    response = session.get("https://" + server + "/" + opt, verify=False)
    return response.content


rawResponse = getResponse(VROPSIP, "/suite-api/api/alerts/types", VROPSID, VROPSPW)
xmlResponse = xml.dom.minidom.parseString(rawResponse)
f = open("/var/Collector/data/vrops_types_" + VROPSIP +  ".xml", 'w+')
f.write(xmlResponse.toprettyxml().encode('utf-8'))
f.close()
print("Type collection complete")

