import Queue
import threading
from time import sleep

import os.path as path
import json
import modules.log.syslog as syslog
import modules.cache.cache as cache
from datetime import datetime

import modules.SLApi.vyatta as vyatta

logger = syslog.getLogger(__name__)

#baseFile = "config/base.json"
configFile = "config/slapi-config.json"
devicesFile = 'data/devices.json'

exitFlag = 0

"""
# Example of rule definition:
# .---------------- minute (0 - 59)
# |  .------------- hour (0 - 23)
# |  |  .---------- day of month (1 - 31)
# |  |  |  .------- month (1 - 12)
# |  |  |  |  .---- day of week (0 - 6) (Sunday=0)
# |  |  |  |  |
# *  *  *  *  *
"""
def itsTime2Run(now, rule):
    sch = rule.split()
    run = True
    #minute
    if (sch[0]<>"*"):
        run = False
        minutes = sch[0].split(",")
        for minute in minutes:
            if ("-" in minute):
                range = minute.split("-")
                if (int(range[0])<= now.minute and now.minute <= int(range[1])): run = True
            else:
                if (now.minute == int(minute)): run = True
    #hour
    if (sch[1]<>"*" and now.hour <> int(sch[1])): run = False
    #day
    if (sch[2]<>"*" and now.day <> int(sch[2])): run = False
    #month
    if (sch[3]<>"*" and now.month <> int(sch[3])): run = False
    #week
    if (sch[4]<>"*"):
        if (now.weekday()==0): w=0
        else: w=now.weekday()+1
        if (w <> int(sch[4])): run = False
    return run

# Thread class
class collectorThread (threading.Thread):
    def __init__(self, threadID, name, q, stateDataQueue):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
        self.stateDataQueue = stateDataQueue
    def run(self):
        logger.debug( "Starting thread " + self.name )
        process_data(self.name, self.q)
        logger.debug( "Exiting thread " + self.name )

# Thread process data function
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
                    history={}
                    history['timestamp']=datetime.now().strftime("%Y%m%d%H%M%S")
                    history['account_id']=base['account_id']
                    history['device']=data['fullyQualifiedDomainName']
                    history['product']="Vyatta"
                    history['item']="UpDown"
                        
                    #print data['primaryBackendIpAddress'] + " " + password
                    vrrpTxt = vyatta.getVyattaInfo(data['fullyQualifiedDomainName'], data['primaryBackendIpAddress'],"vyatta", password, "show vrrp")
                    upDown = vyatta.parseUpDown(vrrpTxt)
                    if (upDown == 0):
                        # is down
                        #print data['fullyQualifiedDomainName'] + " is down"
                        logger.debug(vrrpTxt + " " + data['fullyQualifiedDomainName'] + " is down")
                        history['value']='down'
                    elif (upDown == 1):
                        # is up and master vrrp
                        #print data['fullyQualifiedDomainName'] + " is up and master"
                        vpnStatusTxt = vyatta.getVyattaInfo(data['fullyQualifiedDomainName'], data['primaryBackendIpAddress'],"vyatta", password, "show vpn ipsec sa")
                        vpnStatusTxt = vpnStatusTxt.split("\n")
                        vpnStatus =  vyatta.parseVPN(vpnStatusTxt)
                        
                        historyVPN={}
                        historyVPN['timestamp']=datetime.now().strftime("%Y%m%d%H%M%S")
                        historyVPN['account_id']=base['account_id']
                        historyVPN['device']=data['fullyQualifiedDomainName']
                        historyVPN['product']="Vyatta"
                        historyVPN['item']="VPN"
                        historyVPN['value']=vpnStatus
                        cache.dumpHistory(historyVPN)
                        
                        # Add to queue evaluation change state (VPN)
                        for vpn in vpnStatus:
                            for tunnel in vpn['Tunnel']:
                                for key, value in tunnel.iteritems():
                                    #print key, value
                                    vpnQueue={}
                                    vpnQueue['timestamp']=historyVPN['timestamp']
                                    vpnQueue['account_id']=historyVPN['account_id']
                                    vpnQueue['device']=historyVPN['fullyQualifiedDomainName']
                                    vpnQueue['product']="Vyatta"
                                    vpnQueue['item'] = vpn['Description']+" PeerID:"+vpn['PeerID']+" LocalID:"+vpn['LocalID']+" Tunnel:"+key
                                    vpnQueue['value'] = value
                                    #Add to queue
                                    stateDataQueueLock.acquire()
                                    self.stateDataQueue.put(vpnQueue)
                                    stateDataQueueLock.release()

                        #print vpnStatus
                        logger.debug(data['fullyQualifiedDomainName'] + " is up and master")
                        history['value']='up-master'
                        
                    else:
                        logger.debug(data['fullyQualifiedDomainName'] + " is up and backup")
                        history['value']='up-backup'
                        
                    cache.dumpHistory(history)
                    
                    # Add to queue evaluation change state (UpDown)
                    stateDataQueueLock.acquire()
                    self.stateDataQueue.put(history)
                    stateDataQueueLock.release()
                else:
                    logger.error("Cant retrieve " + data['fullyQualifiedDomainName'] + " authentication")
        else:
            queueLock.release()
            sleep(1)

################################################################################
"""
# Load base configuration (account_id)
if path.exists(baseFile):
    with open(baseFile) as infile:
        base = json.load(infile)
    logger.info('Base configuration loaded.')
else:
    logger.error('Not able to retrieve config/base.json')
    sys.exit()
"""    
# Load base configuration (account_id)
if path.exists(configFile):
    with open(configFile) as infile:
        config = json.load(infile)
    logger.info('Configuration loaded.')
else:
    logger.error('Not able to retrieve '+configFile)
    sys.exit()
    
# Creating state device evaluation thread
stateDataQueueLock = threading.Lock()
stateDataQueue = Queue.Queue(0)
threadEval = slack.evaluateStateThread("Evaluation State Thread", stateDataQueue, stateDataQueueLock, config['CUSTOMER'])
threadEval.start()

# Creating parallel schedule threads 
threadList = ["Thread-1", "Thread-2", "Thread-3", "Thread-4", "Thread-5", "Thread-6", "Thread-7", "Thread-8", "Thread-9", "Thread-10"]
#nameList = ["One", "Two", "Three", "Four", "Five"]
queueLock = threading.Lock()
#workQueue = Queue.Queue(10)
workQueue = Queue.Queue(0)
threads = []
threadID = 1
# Create new threads
for tName in threadList:
    thread = collectorThread(threadID, tName, workQueue, stateDataQueue)
    thread.start()
    threads.append(thread)
    threadID += 1
    
#minute trigger (infinite loop)
while (True):
    # Load device list scheduler
    if (path.exists(devicesFile)):
        with open(devicesFile) as infile:
            devices = json.loads(json.load(infile))
    
        #check each schedule for each device 
        for device in devices:
            now = datetime.now()
            
            for item in device['schedules']:
                #all scheduled itens
                for index in range(len(item.keys())):
                    monitor = item.keys()[index]
                    rule = item[monitor]['rule']
                    enable = item[monitor]['enable'].upper()=="TRUE"
                    #if reach the schedule time put schedule job in the queue
                    if (enable and itsTime2Run(now, rule)):
                        #print `device['id']` + " " + monitor
                        queueLock.acquire()
                        workQueue.put(device)
                        queueLock.release()
    else:
        logger.error("Devices file "+devicesFile+" doesnt exist!")
        sys.exit()
    
    logger.info("Sleeping  runCollector...")
    sleep( 60-datetime.now().second )