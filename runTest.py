import requests
import json

URL="https://hooks.slack.com/services/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"
headers = {'Content-type': 'application/json'}
preText = "BRF"+ "-fnvya005.brf.xxx-down" 
payload = {"username": "ISSD-BOT", 'color': 'warning', 'text': preText , 'fields': [{"title": "Customer", "value": "Test Customer", "short": True}, {"title": "Product", "value": "Teste Product", "short": True}, {"title": "Device", "value": "Test Dev", "short": True}, {"title": "Item", "value": "Test Item", "short": True}, {"title": "Prior State", "value": "Test", "short": True}, {"title": "New State", "value": "Test", "short": True}]}

try:
    response = requests.post(URL, data=json.dumps(payload), headers=headers, verify=False)
    print "Sent slack message: "
except requests.exceptions.ConnectionError:
    print "Error sending message to Slack.com"