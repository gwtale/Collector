#https://hooks.slack.com/services/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
import Queue
import threading
import requests
import json
from time import sleep
import modules.log.syslog as syslog
#from atk import StateSet

logger = syslog.getLogger(__name__)

URL="https://hooks.slack.com/services/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"
headers = {'Content-type': 'application/json'}

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
                            changeStateMsg = {"username": "ISSD-BOT", 'color': color, 'fields': [{"title": "Customer", "value": self.customer, "short": True}, {"title": "Product", "value": data['product'], "short": True}, {"title": "Device", "value": data['device'], "short": True}, {"title": "Item", "value": data['item'], "short": True}, {"title": "Prior State", "value": state['value'], "short": True}, {"title": "New State", "value": data['value'], "short": True}]}
                            #changeStateMsg = "Customer: " + self.customer+" | Product: "+data['product']+" | Device: "+data['device']+" | Item: "+data['item']+" | Old State: "+state['value']+" | New State: "+data['value']
                            #change the actual state
                            self.states[pos]['value']=data['value']
                            
                            # Add alert message in the queue
                            #print changeStateMsg
                            logger.info("Adding alert do queue: "+changeStateMsg)
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
                payload = message
                try:
                    response = requests.post(URL, data=json.dumps(payload), headers=headers, verify=False)
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
