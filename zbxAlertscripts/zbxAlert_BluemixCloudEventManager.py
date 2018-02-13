#!/usr/bin/python
import syslog
import ast
import sys
import requests
import getpass

payload = None
result = None
user = getpass.getuser()

syslog.syslog(syslog.LOG_INFO, str(user) + ': Processing started')
print("Processing started")
#logger.debug('zbxRequests.py: Processing started')

def convertSevToCEM(payload):
    severityTable = {
        "Not classified":"Indeterminate",
        "Information":"Information",
        "Warning":"Warning",
        "Average":"Minor",
        "High":"Major",
        "Disaster":"Critical"
    }
    payload['data']['severity'] = severityTable[str(payload['data']['severity'])]
    return payload

def convertZabbixDateToMySql(date):
    date = date.replace(".", "-")
    return date

def httpGet(payload):
    r = ""
    syslog.syslog(syslog.LOG_DEBUG, str(user) + ": About to execute GET against " + str(payload["url"]) + " with the following data: \n" + str(payload["data"]))
    print(str(user) + ": About to execute GET against " + str(payload["url"]) + " with the following data: \n" + str(payload["data"]))
    try:
        if "id" in payload:
            r = requests.get(payload["url"], params=payload["data"], auth = HTTPBasicAuth(payload["id"], payload["password"]))
        else:
            r = requests.get(payload["url"], params=payload["data"])
    except Exception as e:
        print("Error performing GET: " + str(e))
        syslog.syslog(syslog.LOG_ERR, str(user) + ": Error performing GET: " + str(e))

def httpPost(payload):
    r = ""
    syslog.syslog(syslog.LOG_DEBUG, str(user) + ": About to execute POST against " + str(payload["url"]) + " with the following data: \n" + str(payload["data"]))
    print(str(user) + ": About to execute POST against " + str(payload["url"]) + " with the following data: \n" + str(payload["data"]))
    try:
        if "id" in payload: 
            print("ID: " + str(payload["id"]))
            r = requests.post(payload["url"], json = payload["data"], auth = (payload["id"], payload["password"]))
            print("Reply from server: " + str(r.text))
        else:
            r = requests.post(payload["url"], data = payload["data"])
        print r
    except Exception as e:
        print("Error performing POST: " + str(e))
        syslog.syslog(syslog.LOG_ERR, str(user) + ": Error performing POST: " + str(e))

# Receive data from Zabbix
payload = sys.argv[1]
syslog.syslog(syslog.LOG_DEBUG, str(user) + ": payload: ")
syslog.syslog(syslog.LOG_DEBUG, str(user) + ": " + payload)

try:
    payload = sys.argv[1]
    payload = ast.literal_eval(payload) 
    if "severity" in payload['data']:
        payload = convertSevToCEM(payload)
    if "timestamp" in payload['data']:
        payload['data']['timestamp'] = convertZabbixDateToMySql(payload['data']['timestamp'])

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

