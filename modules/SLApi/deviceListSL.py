"""
Created on Mar 31, 2016

@author: jpmenega
"""
import requests
import json
import os.path
import modules.log.syslog as syslog

logger = syslog.getLogger(__name__)

devicesFile = 'data/devices.json'


def updateDeviceListFromSL(config):
    USER = config['USER']
    USER_KEY = config['USER_KEY']
    SERVER = config['SERVER']
    REST_HARDWARE = config['REST_HARDWARE']
    REST_VIRTUAL_GUESTS = config['REST_VIRTUAL_GUESTS']
    
    logger.info("Updating local device list...")
    
    inError = False
    
    deviceListSL = []
    
    logger.debug("Loading Hardware (Bare Metal) list from SL...")
    response = requests.get("https://"+USER+":"+USER_KEY+"@"+SERVER+REST_HARDWARE)
    if (response.status_code == 200):
        logger.debug("Hardware list received with success!")
        hardwareListSL = json.loads(response.content)
        
        for hardwareSL in hardwareListSL:
            deviceSL = {}
            deviceSL['type']='BareMetal'
            deviceSL['id']=hardwareSL['id']
            deviceSL['fullyQualifiedDomainName']=hardwareSL['fullyQualifiedDomainName']
            deviceSL['primaryBackendIpAddress']=hardwareSL['primaryBackendIpAddress']
            
            isIdera = False
            softwareComponents = hardwareSL['softwareComponents']
            for softwareComponent in softwareComponents:
                #if ('passwords' in softwareComponent):
                #    for user in softwareComponent['passwords']:
                #        username = user['username']
                #        password = user['password']
                #        logger.debug("* "+hardwareSL['fullyQualifiedDomainName']+" "+username+" "+password)
                #        logger.debug("* "+softwareComponent['softwareLicense']['softwareDescription']['longDescription'])
                if ('softwareLicense' in softwareComponent and softwareComponent['softwareLicense']['softwareDescription']['manufacturer'] == 'Idera'):
                    isIdera = True
                    break
            
            if (isIdera):
                deviceSL['product'] = 'Idera'
            else:
                deviceSL['product'] = hardwareSL['operatingSystem']['softwareLicense']['softwareDescription']['manufacturer']
            
            users = []
            if (len(hardwareSL['operatingSystem']['passwords'])<>0):
                for user in hardwareSL['operatingSystem']['passwords']:
                    username = user['username']
                    password = user['password']
                    users.append({username: password})
                    #logger.debug(hardwareSL['fullyQualifiedDomainName']+" "+username+" "+password)
            deviceSL['users']=users
            deviceListSL.append(deviceSL)
    else:
        logger.error('Error loading Hardware list from SoftLayer. Devices list is out of date!')
        inError = True    
    
    logger.debug("Loading Virtual Guests list from SL...")
    response = requests.get("https://"+USER+":"+USER_KEY+"@"+SERVER+REST_VIRTUAL_GUESTS)
    if (response.status_code == 200):
        logger.debug("Virtual Guests list received with success!")
        virtualGuestsListSL = json.loads(response.content)
        for virtualGuestSL in virtualGuestsListSL:
            deviceSL = {}
            deviceSL['type']='Virtual'
            deviceSL['id']=virtualGuestSL['id']
            deviceSL['fullyQualifiedDomainName']=virtualGuestSL['fullyQualifiedDomainName']
            deviceSL['primaryBackendIpAddress']=virtualGuestSL['primaryBackendIpAddress']
            
            isIdera = False
            softwareComponents = virtualGuestSL['softwareComponents']
            for softwareComponent in softwareComponents:
                if ('softwareLicense' in softwareComponent and softwareComponent['softwareLicense']['softwareDescription']['manufacturer'] == 'Idera'):
                    isIdera = True
                    break
            
            if (isIdera):
                deviceSL['product'] = 'Idera'
            else:
                deviceSL['product'] = virtualGuestSL['operatingSystem']['softwareLicense']['softwareDescription']['manufacturer']
            
            users = []
            if (len(virtualGuestSL['operatingSystem']['passwords'])<>0):
                for user in virtualGuestSL['operatingSystem']['passwords']:
                    username = user['username']
                    password = user['password']
                    users.append({username: password})
                    #logger.debug(virtualGuestSL['fullyQualifiedDomainName']+" "+username+" "+password)
            deviceSL['users']=users
            deviceListSL.append(deviceSL)
    else:
        logger.error('Error loading Virtual Guests list from SoftLayer. Devices list is out of date!')
        inError = True

    #Update local list
    if (not inError):
        logger.debug("Compare data...")
        
        #Verifica se jah existe o arquivo de configuracoes para a conta, senao existe entao irah criar um novo
        if (os.path.exists(devicesFile)):
            with open(devicesFile) as infile:
                devicesListLocal = json.loads(json.load(infile))
        else:
            devicesListLocal = []
            
        deviceUp2dateList = []
        #Verifica se o hardware da lista local ainda existe na SL, se nao existir mais ignora/exclui da nova lista    
        for deviceLocal in devicesListLocal:
            encontrou = False
            for deviceSL in deviceListSL:
                #Se hardware jah existe soh mantem ele na lista sem alteracoes
                if (deviceSL['id'] == deviceLocal['id']):
                    encontrou = True
                    deviceUp2date = {}
                    deviceUp2date['id'] = deviceLocal['id']
                    if (deviceSL['type'] <> deviceLocal['type']):
                        deviceUp2date['type'] = deviceSL['type']
                        logger.info("Device ID:" + `deviceLocal['id']` + ' Old Type: ' + deviceLocal['type'] + ' New Type: '+deviceSL['type']) 
                    else:
                        deviceUp2date['type'] = deviceLocal['type']
                        
                    if (deviceSL['fullyQualifiedDomainName'] <> deviceLocal['fullyQualifiedDomainName']):
                        deviceUp2date['fullyQualifiedDomainName'] = deviceSL['fullyQualifiedDomainName']
                        logger.info("Device ID:" + `deviceLocal['id']` + ' Old FQDN: ' + deviceLocal['fullyQualifiedDomainName'] + ' New FQDN: '+deviceSL['fullyQualifiedDomainName']) 
                    else:
                        deviceUp2date['fullyQualifiedDomainName'] = deviceLocal['fullyQualifiedDomainName']
                        
                    if (deviceSL['product'] <> deviceLocal['product']):
                        deviceUp2date['product'] = deviceSL['product']
                        logger.info("Device ID:" + `deviceLocal['id']` + ' Old Product: ' + deviceLocal['product'] + ' New Product: '+deviceSL['product']) 
                    else:
                        deviceUp2date['product'] = deviceLocal['product']
                        
                    if (deviceSL['primaryBackendIpAddress'] <> deviceLocal['primaryBackendIpAddress']):
                        deviceUp2date['primaryBackendIpAddress'] = deviceSL['primaryBackendIpAddress']
                        logger.info("Device ID:" + `deviceLocal['id']` + ' Old IP Address: ' + deviceLocal['primaryBackendIpAddress'] + ' New IP Address: '+deviceSL['primaryBackendIpAddress']) 
                    else:
                        deviceUp2date['primaryBackendIpAddress'] = deviceLocal['primaryBackendIpAddress']
                        
                        
                    deviceUp2date['users'] = deviceSL['users']

                    deviceUp2dateList.append(deviceUp2date)
                    
                    break
            if (not encontrou):
                logger.info("Removing Device ID:" + `deviceLocal['id']` + ' Type: ' + deviceLocal['type'] + ' FQDN: ' + deviceLocal['fullyQualifiedDomainName'])
            
        #Verifica se algum dispositivo ainda nao entrou na nova lista, isso significa que eh um novo dispositivo    
        for deviceSL in deviceListSL:
            jaExiste = False
            for deviceUp2date in deviceUp2dateList:
                #Se o hardware jah existe na lista entao soh ignora
                if (deviceUp2date['id'] == deviceSL['id']):
                    jaExiste = True
                    break
            #Se nao existe trata-se de um novo device
            if (not jaExiste):
                logger.info("Adding Device ID:" + `deviceSL['id']` + ' Type: ' + deviceSL['type'] + ' FQDN: ' + deviceSL['fullyQualifiedDomainName'])

                deviceUp2dateList.append(deviceSL)
                
        #Salva arquivo de configuracoes     
        with open(devicesFile, 'w') as outfile:
            json.dump( json.dumps(deviceUp2dateList) , outfile)

    return