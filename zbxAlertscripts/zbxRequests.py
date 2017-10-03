#!/usr/bin/python

"""
Supported methods: get, post

Payload examples (run them with ./zbxRequests.py " <paste payload here> "):
{
    \"method\":\"post\",
    \"url\":\"http://192.168.10.128/ibmcloudtkt2/ezexpedite/insertTicket.api.php\",
    \"data\":{
        \"ttype1\":\"2\",
        \"sender\":\"gts-is-sl@wwpdl.vnet.ibm.com\",
        \"cod_user\":\"0\",
        \"cod_sender\":\"3819\",
        \"cod_team\":\"0\",
        \"var\":\"PROBLEM\",
        \"tkt_number\":\"1899582\",
        \"severity\":\"Disaster\",
        \"ncustomer\":\"Livelo\",
        \"sdescr\":\"TEST TEST TEST\",
        \"info\":\"<a href='http://208.43.238.157:9998/zabbix/tr_events.php?triggerid=123&eventid=123' target='_blank'>See on Zabbix</a>\",
        \"server\":\"fnnvya001liv.pontoslivelo.com.\",
        \"OpenDate\":\"2016.09.10 12:07:22\"
    }
}

{
    \"method\":\"post\",
    \"url\":\"http://192.168.10.128/ibmcloudtkt2/ezexpedite/insertTicket.api.php\",
    \"data\":{
        \"ttype1\":\"2\",
        \"sender\":\"gts-is-sl@wwpdl.vnet.ibm.com\",
        \"cod_user\":\"3819\",
        \"cod_sender\":\"3819\",
        \"cod_team\":\"0\",
        \"var\":\"OK\",
        \"tkt_number\":\"1899582\",
        \"severity\":\"Disaster\",
        \"ncustomer\":\"Livelo\",
        \"sdescr\":\"TEST TEST TEST\",
        \"info\":\"\",
        \"server\":\"fnnvya001liv.pontoslivelo.com.\",
        \"resolution\":\"Problem is now resolved, either by an analyst or automatically by Zabbix.\",
        \"CloseDate\":\"2016.09.12 12:07:22\"
    }
}
"""
import syslog
import ast
import sys
import requests
import getpass
#import logging
#import logging.handlers

#logger = logging.getLogger('zbxRequests.py')
#logger.setLevel(logging.DEBUG)
#handler = logging.handlers.SysLogHandler(address = '/dev/log')
#logger.addHandler(handler)

payload = None
result = None
user = getpass.getuser()

syslog.syslog(syslog.LOG_INFO, str(user) + ': Processing started')
print("Processing started")
#logger.debug('zbxRequests.py: Processing started')

def convertSevToNum(payload):
    severityNum = {
        "Warning":4,
        "Average":3,
        "High":2,
        "Disaster":1
    }
    payload['data']['severity'] = severityNum[str(payload['data']['severity'])]
    return payload

def convertZabbixDateToMySql(date):
    date = date.replace(".", "-")
    return date

def httpGet(payload):
    syslog.syslog(syslog.LOG_DEBUG, str(user) + ": About to execute GET against " + str(payload["url"]) + " with the following data: \n" + str(payload["data"]))
    try:
        r = requests.get(payload["url"], params=payload["data"])
        syslog.syslog(syslog.LOG_DEBUG, str(user) + ": RESULT: Status code: " + str(r.status_code) + ", Message from server: " + str(r.text))
    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, str(user) + ": Error performing GET: Status code: " + str(r.status_code) + ", Message from server: " + str(r.text))

def httpPost(payload):
    syslog.syslog(syslog.LOG_DEBUG, str(user) + ": About to execute POST against " + str(payload["url"]) + " with the following data: \n" + str(payload["data"]))
    try:
        r = requests.post(payload["url"], data = payload["data"])
        syslog.syslog(syslog.LOG_DEBUG, str(user) + ": RESULT: Status code: " + str(r.status_code) + ", Message from server: " + str(r.text))
    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, str(user) + ": Error performing POST: Status code: " + str(r.status_code) + ", Message from server: " + str(r.text))
        print("Error performing POST: Status code: " + str(r.status_code) + ", Message from server: " + str(r.text))

# Receive data from Zabbix
payload = sys.argv[1]
syslog.syslog(syslog.LOG_DEBUG, str(user) + ": payload: ")
syslog.syslog(syslog.LOG_DEBUG, str(user) + ": " + payload)

try:
    payload = sys.argv[1]
    payload = ast.literal_eval(payload) 
    if "severity" in payload['data']:
        payload = convertSevToNum(payload)
    if "OpenDate" in payload['data']:
        payload['data']['OpenDate'] = convertZabbixDateToMySql(payload['data']['OpenDate'])
    if "CloseDate" in payload['data']:
        payload['data']['CloseDate'] = convertZabbixDateToMySql(payload['data']['CloseDate'])
except Exception as e:
    syslog.syslog(syslog.LOG_ERR, str(user) + ": Error processing received payload: " + str(e))
    print("Error processing received payload: " + str(e))
    sys.exit(1)

# Parse GET or POST
if "method" in payload:
    if payload['method'] == "post":
        result = httpPost(payload)
    elif payload['method'] == "get":
        result = httpGet(payload)
    else:
        syslog.syslog(syslog.LOG_ERR, str(user) + ": HTTP request method unknown: " + str(payload['method']))
        print("HTTP request method unknown: " + str(payload['method']))
        sys.exit(1)
else:
    syslog.syslog(syslog.LOG_ERR, str(user) + ": HTTP request method unknown.")
    print("HTTP request method unknown")
    sys.exit(1)

