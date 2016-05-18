#https://www.brocade.com/content/dam/common/documents/content-types/api-reference-guide/vyatta-remote-access-api-3.5r3-v01.pdf

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import time

import json
import base64

import modules.log.syslog as syslog

logger = syslog.getLogger(__name__)

#disable HTTPS certificates warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def getVyattaInfo(FQDN, URL, USER, PASSWORD, COMMAND):
    headers = {'Accept': 'application/json', 
               'Vyatta-Specification-Version': '0.1', 
               'Authorization': 'Basic '+base64.b64encode(USER+':'+PASSWORD)}
    
    restVyattaCommand = COMMAND.replace(" ","/")
    logger.debug("Vyatta operational command: "+COMMAND)
    #response = requests.get("https://"+URL+"/rest/op", headers=headers, verify=False)
    tries = 2
    ret = 0
    while (tries > 0 and ret<>201):
        try:
            response = requests.post("https://"+URL+"/rest/op/"+restVyattaCommand, headers=headers, verify=False)
            ret = response.status_code
        except requests.exceptions.ConnectionError as e:
            logger.error("getVyattaInfo: Error trying contacting Vyatta "+FQDN+"! "+e)
            #return "ERROR: Error contacting Vyatta!"
        tries -= 1

    if (ret == 201): #201
        location = response.headers['Location']
        tries = 2
        ret = 0
        while (tries > 0 and ret<>200):
            try:
                response = requests.get("https://"+URL+"/"+location, headers=headers, verify=False)
                ret = response.status_code
                if (ret == 202 and tries > 1):
                    time.sleep(2)
            except requests.exceptions.ConnectionError as e:
                logger.error("getVyattaInfo: Error trying contacting Vyatta "+FQDN+"! "+e)
                #return "ERROR: Error contacting Vyatta!"
            tries -= 1
            
        if (ret == 200): #200
            #logger.debug(response.content)
            infoRet = response.content
            logger.debug("getVyattaInfo: Query executed with success!")
            
            try:
                response = requests.delete("https://"+URL+"/"+location, headers=headers, verify=False)
                ret = response.status_code
                if (ret <> 200):
                    logger.error("getVyattaInfo: Error cleaning Vyatta "+FQDN+" command buffer!. HTTP Error code: "+`ret`)
            except requests.exceptions.ConnectionError  as e:
                logger.error("getVyattaInfo: Error contacting Vyatta "+FQDN+" to clear buffer command! "+`ret`+" "+e)

            return infoRet
        else:
            if (ret == 410): #vyatta nao tem VPN
                logger.debug("getVyattaInfo: Vyatta "+FQDN+" dont have VPN!. HTTP Error code: "+`ret`)
                return "ERROR: Vyatta dont have VPN!"
            else:
                logger.error("getVyattaInfo: Error getting Vyatta "+FQDN+" command results!. HTTP Error code: "+`ret`)
                return "ERROR: Error getting Vyatta command results!"
    else:
        logger.error("getVyattaInfo: Error sending Vyatta "+FQDN+" commands!. HTTP Error code: "+`ret`)
        return "ERROR: Error sending Vyatta commands!"

    
def parseVPN(status):
    skipLine = 0
    newPeer = False
    newDescription = False
    newTunnel = False
    
    vpns = []
    
    for line in status:
        if (skipLine == 0):
            if (newTunnel):
                if (line == ''):
                    newTunnel = False
                    
                    vpn['Tunnel']=tunnel

                    #newVpn={'peer': vpn}
                    if (peerID!="0.0.0.0"):
                        vpns.append(vpn)
                else:
                    newLine = line.strip() 
                    idx = newLine.index(' ')
                    id = newLine[:idx]
                    
                    newLine = newLine[idx:].strip()
                    idx = newLine.index(' ')
                    status = newLine[:idx]
                    #print "Tunnel ID: "+id
                    #print "Tunnel Status: "+status
                    tunnel.append({id: status})
                    
                
            if (newPeer):
                newPeer = False
                peerID = line[:line.index(' ')]
                localID = ((line[line.index(' '):]).replace(" ", ""))
                #print "Peer ID / IP: "+peerID
                #print "Local ID / IP: "+localID
                #print ord(localID[12])
                vpn = {}
                vpn['PeerID']=peerID
                vpn['LocalID']=localID
                #vpn['Tunnel']=[]
                tunnel = []
                
                skipLine = 1
                #newDescription = True
                
            if (line.startswith('Peer ID / IP')):
                newPeer = True
                skipLine = 1
            elif (line.strip().startswith('Description')):
                description = (line.replace("Description:","")).strip()
                vpn['Description']=description
                #print "Description: "+description
            elif (line.strip().startswith('Tunnel')):
                newTunnel = True
                skipLine = 1
        else:
            skipLine = skipLine - 1
        #logger.info(line)
        #print line,
    return vpns

#Returns
#0: Down
#1: Up and Master
#2: Up and Backup
def parseUpDown(vrrpTxt):
    if (vrrpTxt.startswith("ERROR:")):
        #print "Error contacting Vyatta"
        return 0
    elif (" BACKUP " in vrrpTxt):
        #print "Vyatta Backup"
        return 2
    elif (" MASTER " in vrrpTxt):
        #print "Vyatta Master"
        return 1
    else:
        return 0