#https://hooks.slack.com/services/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
import Queue
import threading
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json
from time import sleep
import modules.log.syslog as syslog
#from atk import StateSet

logger = syslog.getLogger(__name__)

#Slack_URL="https://hooks.slack.com/services/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"
#headers = {'Content-type': 'application/json'}

Slack_URL="https://slack.com/api/chat.postMessage"
Slack_channel="#softlayer_alerts"
#Slack_channel="#softlayer_dev"
Slack_username="softlayermon"


# Thread class
class evaluateStateThread (threading.Thread):
    def __init__(self, name, q, queueLock, customer):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q
        self.queueLock = queueLock
        self.customer = customer
        
        self.exitThread = 0
        self.states = []

        #Starts Alert Slack Thread
        self.alertsQueue = Queue.Queue(0)        
        self.threadAlerts = slackAlertsThread("Alert Slack Thread", self.alertsQueue, self.queueLock)
        self.threadAlerts.start()

    def run(self):
        logger.debug( "Starting thread " + self.name )

        while (not self.exitThread):
            self.queueLock.acquire()
            if not self.q.empty():
                data = self.q.get()
                self.queueLock.release()
                
                #check if item is in the list and change value if something changed
                pos = 0
                foundState = 0
                for state in self.states:
                    if (state['device'] == data['device'] and state['item'] == data['item']):
                        if ( state['value']<>data['value']):
                            color = "good"
                            if ("DOWN" in data['value'].upper()):
                                color = "danger"
                            preText = self.customer+ " - "+ data['device'] + " - " + data['value'] 
                            #changeStateMsg = {"username": "ISSD-BOT", 'color': color, 'text': preText , 'fields': [{"title": "Customer", "value": self.customer, "short": True}, {"title": "Product", "value": data['product'], "short": True}, {"title": "Prior State", "value": state['value'], "short": True}, {"title": "New State", "value": data['value'], "short": True}, {"title": "Device", "value": data['device'], "short": False}, {"title": "Item", "value": data['item'], "short": False}]}
                            changeStateMsg = {'text': preText , 'color': color, 'fields': [{"title": "Customer", "value": self.customer, "short": True}, {"title": "Product", "value": data['product'], "short": True}, {"title": "Prior State", "value": state['value'], "short": True}, {"title": "New State", "value": data['value'], "short": True}, {"title": "Device", "value": data['device'], "short": False}, {"title": "Item", "value": data['item'], "short": False}]}
                            changeStateTxt = "Customer: " + self.customer+" | Product: "+data['product']+" | Device: "+data['device']+" | Item: "+data['item']+" | Old State: "+state['value']+" | New State: "+data['value']
                            
                            #change the actual state
                            self.states[pos]['value']=data['value']
                            
                            # Add alert message in the queue
                            #print changeStateMsg
                            logger.info("Adding alert to queue: "+changeStateTxt)
                            self.queueLock.acquire()
                            self.alertsQueue.put(changeStateMsg)
                            self.queueLock.release()
                            
                        foundState = 1                                                
                        break
                    pos += 1
                
                if (not foundState):
                    self.states.append(data)
                    #print "New item: "+data['device']
            else:
                self.queueLock.release()
                sleep(5)
        
        # Wait alerts thread to finish
        self.threadAlerts.join()
                
        logger.debug( "Exiting thread " + self.name )
    
    def exitEvaluateAlertsThread(self):
        self.threadAlerts.exitSlackAlertsThread()
        self.exitThread = 1

# Thread class
class slackAlertsThread (threading.Thread):
    def __init__(self, name, q, queueLock):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q
        self.queueLock = queueLock
        
        self.exitThread = 0
    def run(self):
        logger.debug( "Starting thread " + self.name )
        
        aliveThread = 1
        while (aliveThread):
            
            self.queueLock.acquire()
            if not self.q.empty():
                message = self.q.get()
                self.queueLock.release()
        
                #process_data(self.name, self.q)
                #payload = {"username": "ISSD-BOT", 'text': message}
                #payload = message       
                text = message.pop('text', None)
                #print json.dumps(message)  
                payload = MultipartEncoder(
                        fields={'token': 'xoxb-49553493588-6Fxbn38CaJft1OcARPzOP5il',
                                 "channel": Slack_channel,
                                 "username": Slack_username,
                                 "text": text,
                                'attachments': '['+json.dumps(message)+']'})
                headers = {'Content-type': payload.content_type}
                
                            #if (payload['color'] == "danger"):
                            #    #new issue
                            #    changeStateMsg = MultipartEncoder(
                            #        fields={'token': 'xoxb-49553493588-6Fxbn38CaJft1OcARPzOP5il',
                            #                 "channel": Slack_channel,
                            #                 "username": Slack_username,
                            #                 "text": preText,
                            #                 'attachments': '['+json.dumps(attachment)+']'}
                            #        )
                            #else:
                            #    #delete issue
                            #    changeStateMsg = MultipartEncoder(
                            #        fields={'token': 'xoxb-49553493588-6Fxbn38CaJft1OcARPzOP5il',
                            #                 "channel": "",
                            #                 "username": Slack_username,
                            #                 "ts": ""}
                            #        )
                
                try:
                    #response = requests.post(Slack_URL, data=json.dumps(payload), headers=headers, verify=False)
                    response = requests.post(Slack_URL, data=payload, headers=headers, verify=False)
                    #logger.info("Sent slack message: "+message)
                    logger.debug("Sent slack message")
                except requests.exceptions.ConnectionError:
                    logger.error("Error sending message to Slack.com")
    
                sleep(1)
            else:
                self.queueLock.release()
                if (self.exitThread):
                    aliveThread = 0 #exit thread only when the queue is empty
                else:
                    sleep(10)
        
        logger.debug( "Exiting thread " + self.name )
    
    def exitSlackAlertsThread(self):
        self.exitThread = 1
