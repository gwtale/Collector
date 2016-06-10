import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json

#URL="https://hooks.slack.com/services/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"
URL="https://slack.com/api/chat.postMessage"
#URL="https://slack.com/api/chat.update"
#URL="https://slack.com/api/chat.delete"
#preText = "TEST"+ "-fnvya005.brf.xxx-down" 
#payload = {"username": "ISSD-BOT", 'color': 'warning', 'text': preText , 
#           'fields': [{"title": "Customer", "value": "Test Customer", "short": True}, 
#                      {"title": "Product", "value": "Teste Product", "short": True}, 
#                      {"title": "Prior State", "value": "Test", "short": True}, 
#                      {"title": "New State", "value": "Test", "short": True},
#                      {"title": "Device", "value": "fnnvya001liv.pontoslivelo.com.br", "short": False},
#                      {"title": "Item", "value": "VPN to PayTrue in Uruguay\nPeerID:190.64.82.58\nLocalID:169.55.23.43\nTunnel:6", "short": False}]}

attachment = {'color': 'warning', 
           'fields': [{"title": "Customer", "value": "Test Customer", "short": True}, 
                      {"title": "Product", "value": "Teste Product", "short": True}, 
                      {"title": "Prior State", "value": "Test", "short": True}, 
                      {"title": "New State", "value": "Test", "short": True},
                      {"title": "Device", "value": "fnnvya001liv.pontoslivelo.com.br", "short": False},
                      {"title": "Item", "value": "VPN to PayTrue in Uruguay\nPeerID:190.64.82.58\nLocalID:169.55.23.43\nTunnel:6", "short": False}]}

payload = MultipartEncoder(
    fields={'token': 'xoxb-49553493588-6Fxbn38CaJft1OcARPzOP5il',
             "channel": "C0RM6RMGF",
             "username": "softlayermon",
             "ts": "1465499684.000048"}
    )
payload = MultipartEncoder(
    fields={'token': 'xoxb-49553493588-6Fxbn38CaJft1OcARPzOP5il',
             "channel": "C0RM6RMGF",
             "text": "update msg",
             "username": "softlayermon",
             "ts": "1465499684.000048"}
    )
payload = MultipartEncoder(
    fields={'token': 'xoxb-49553493588-6Fxbn38CaJft1OcARPzOP5il',
             "channel": "#softlayer_alerts",
             "username": "softlayermon",
             "text": "pre text 2",
             'attachments': '['+json.dumps(attachment)+']'}
    )
headers = {'Content-type': payload.content_type}

#print payload.to_string()
print payload.content_type
try:
    #response = requests.post(URL, data=json.dumps(payload), headers=headers, verify=False)
    response = requests.post(URL, data=payload, headers=headers, verify=False)
    print response.text
    j = json.loads(response.text)
    if (j["ok"]):
        print "ts: "+j["ts"]
        print "channel: "+j["channel"]
    else:
        print "erro"
except requests.exceptions.ConnectionError:
    print "Error sending message to Slack.com"