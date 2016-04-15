#http://www.tutorialspoint.com/python/python_multithreading.htm

import Queue
import threading
import time

import os.path as path
import json
import modules.SLApi.vyatta as vyatta

devicesFile = 'data/devices.json'

exitFlag = 0

class collectorThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print "Starting " + self.name
        process_data(self.name, self.q)
        print "Exiting " + self.name

def process_data(threadName, q):
    while not exitFlag:
        queueLock.acquire()
        if not q.empty():
            data = q.get()
            queueLock.release()
            
            # Category devices
            if (data['product'] == "Vyatta"):
                #print "%s processing %s" % (threadName, data['product'])
                password = ""
                for users in data['users']:
                    if (users.keys()[0] == "vyatta"):
                        password = users[users.keys()[0]]
                        break
                if (password<>""):
                    print data['primaryBackendIpAddress'] + " " + password
                    vrrpTxt = vyatta.getVyattaInfo(data['fullyQualifiedDomainName'], data['primaryBackendIpAddress'],"vyatta", password, "show vrrp")
                    upDown = vyatta.parseUpDown(vrrpTxt)
                    if (upDown == 0):
                        # is down
                        print data['fullyQualifiedDomainName'] + " is down"
                    elif (upDown == 1):
                        # is up and master vrrp
                        print data['fullyQualifiedDomainName'] + " is up"
                        vpnStatusTxt = vyatta.getVyattaInfo(data['fullyQualifiedDomainName'], data['primaryBackendIpAddress'],"vyatta", password, "show vpn ipsec sa")
                        vpnStatus =  vyatta.parseVPN(vpnStatusTxt)
                        print vpnStatus
                else:
                    logger.error("Cant retrieve " + data['fullyQualifiedDomainName'] + " authentication")
        else:
            queueLock.release()
        #time.sleep(1)

threadList = ["Thread-1", "Thread-2", "Thread-3"]
#nameList = ["One", "Two", "Three", "Four", "Five"]
queueLock = threading.Lock()
workQueue = Queue.Queue(10)
threads = []
threadID = 1

# Create new threads
for tName in threadList:
    thread = collectorThread(threadID, tName, workQueue)
    thread.start()
    threads.append(thread)
    threadID += 1

# Load device list
if (path.exists(devicesFile)):
    with open(devicesFile) as infile:
        devicesListLocal = json.loads(json.load(infile))

# Search all Vyatta to collect data (Fill the queue)
for device in devicesListLocal:
    if (device['product'] == "Vyatta"):
        #print device['id']
        queueLock.acquire()
        workQueue.put(device)
        queueLock.release()
        
# Fill the queue
#queueLock.acquire()
#for word in nameList:
#    workQueue.put(word)
#queueLock.release()

# Wait for queue to empty
while not workQueue.empty():
    pass

# Notify threads it's time to exit
exitFlag = 1

# Wait for all threads to complete
for t in threads:
    t.join()
print "Exiting Main Thread"