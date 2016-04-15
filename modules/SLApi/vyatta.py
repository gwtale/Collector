#https://www.brocade.com/content/dam/common/documents/content-types/api-reference-guide/vyatta-remote-access-api-3.5r3-v01.pdf

import requests
import json
import base64

import modules.log.syslog as syslog

logger = syslog.getLogger(__name__)

def getVyattaInfo(URL, USER, PASSWORD, COMMAND):
    headers = {'Accept': 'application/json', 
               'Vyatta-Specification-Version': '0.1', 
               'Authorization': 'Basic '+base64.b64encode(USER+':'+PASSWORD)}
    
    restVyattaCommand = COMMAND.replace(" ","/")
    logger.debug("Vyatta operational command: "+COMMAND)
    #response = requests.get("https://"+URL+"/rest/op", headers=headers, verify=False)
    try:
        response = requests.post("https://"+URL+"/rest/op/"+restVyattaCommand, headers=headers, verify=False)
    except requests.exceptions.ConnectionError:
        logger.error("getVyattaInfo: Error contacting Vyatta!")
        return "ERROR: Error contacting Vyatta!"
        
    if (response.status_code == 201):
        location = response.headers['Location']
        try:
            response = requests.get("https://"+URL+"/"+location, headers=headers, verify=False)
        except requests.exceptions.ConnectionError:
            logger.error("getVyattaInfo: Error contacting Vyatta!")
            return "ERROR: Error contacting Vyatta!"
        if (response.status_code == 200):
            #logger.debug(response.content)
            infoRet = response.content
            logger.debug("getVyattaInfo: Query executed with success!")
            
            try:
                response = requests.delete("https://"+URL+"/"+location, headers=headers, verify=False)
                if (response.status_code <> 200):
                    logger.debug("getVyattaInfo: Error cleaning Vyatta command buffer!. HTTP Error code: "+`response.status_code`)
            except requests.exceptions.ConnectionError:
                logger.debug("getVyattaInfo: Error contacting Vyatta to clear buffer command!"+`response.status_code`)

            return infoRet
        else:
            logger.debug("getVyattaInfo: Error getting Vyatta command results!. HTTP Error code: "+`response.status_code`)
            return "ERROR: Error getting Vyatta command results!"
    else:
        logger.debug("getVyattaInfo: Error sending Vyatta commands!. HTTP Error code: "+`response.status_code`)
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