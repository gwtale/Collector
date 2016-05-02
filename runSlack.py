import Queue
import threading
from time import sleep

import modules.alerts.slack as slack

#slack.set2Slack("Python test message!")

#queueLock = threading.Lock()
#stateQueue = Queue.Queue(0)

stateDataQueueLock = threading.Lock()
stateDataQueue = Queue.Queue(0)

threadEval = slack.evaluateStateThread("Evaluation State Thread", stateDataQueue, stateDataQueueLock, 'BRF')
threadEval.start()


data={}
data['timestamp']='201604281700'
data['account_id']='18'
data['device']='teste.brf.com'
data['product']="Vyatta"
data['item']="UpDown"
data['value']="Up"

stateDataQueueLock.acquire()
stateDataQueue.put(data)
stateDataQueueLock.release()

data={}
data['timestamp']='201604281700'
data['account_id']='18'
data['device']='teste.brf.com'
data['product']="Vyatta"
data['item']="UpDown"
data['value']="Down"

stateDataQueueLock.acquire()
stateDataQueue.put(data)
stateDataQueueLock.release()

data={}
data['timestamp']='201604281700'
data['account_id']='18'
data['device']='teste.brf.com'
data['product']="Vyatta"
data['item']="VPN"
data['value']="VPN xyz PeerID:0.0.0.0 LocalID:1.1.1.1 Tunnel 1: Up"

stateDataQueueLock.acquire()
stateDataQueue.put(data)
stateDataQueueLock.release()

data={}
data['timestamp']='201604281700'
data['account_id']='18'
data['device']='teste.brf.com'
data['product']="Vyatta"
data['item']="VPN"
data['value']="VPN xyz PeerID:0.0.0.0 LocalID:1.1.1.1 Tunnel 1: Down"

stateDataQueueLock.acquire()
stateDataQueue.put(data)
stateDataQueueLock.release()

sleep(8)
threadEval.exitEvaluateAlertsThread()

threadEval.join()

"""
thread = slack.slackAlertsThread("Slack Thread")
thread.start()

sleep(3)
thread.exitSlackAlertsThread()

# Wait thread to complete
thread.join()
"""