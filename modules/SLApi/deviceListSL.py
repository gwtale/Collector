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
    REST_NETSCALER = config['REST_NETSCALER']
    REST_PUBLIC_VLANS = config['REST_PUBLIC_VLANS']
    REST_PUBLIC_VLAN_CHECK_IS_DEDICATED = config['REST_PUBLIC_VLAN_CHECK_IS_DEDICATED']
    REST_PUBLIC_VLAN_FIREWALL = config['REST_PUBLIC_VLAN_FIREWALL']
    REST_PUBLIC_VLAN_FIREWALL_FQDN = config['REST_PUBLIC_VLAN_FIREWALL_FQDN']
    REST_PUBLIC_VLAN_FIREWALL_CREDENTIALS = config['REST_PUBLIC_VLAN_FIREWALL_CREDENTIALS']
    
    
    logger.info("Updating local device list...")
    
    inError = False
    
    deviceListSL = []
    
    logger.debug("Loading Hardware (Bare Metal) list from SL...")
    response = requests.get("https://"+USER+":"+USER_KEY+"@"+SERVER+REST_HARDWARE)
    if (response.status_code == 200):
        logger.debug("Hardware list received with success!")
        hardwareListSL = json.loads(response.content)
        
        for hardwareSL in hardwareListSL:
            if ('primaryBackendIpAddress' in hardwareSL and hardwareSL['primaryBackendIpAddress'] <> ''):
                deviceSL = {}
                deviceSL['type']='BareMetal'
                deviceSL['id']=hardwareSL['id']
                deviceSL['fullyQualifiedDomainName']=hardwareSL['fullyQualifiedDomainName']
                #print hardwareSL
                deviceSL['primaryBackendIpAddress']=hardwareSL['primaryBackendIpAddress']
                deviceSL['networkManagementIpAddress']=hardwareSL['networkManagementIpAddress']
                
                isIdera = False
                softwareComponents = hardwareSL['softwareComponents']
                for softwareComponent in softwareComponents:
                    #if ('passwords' in softwareComponent):
                    #    for user in softwareComponent['passwords']:
                    #        username = user['username']
                    #        password = user['password']
                    #        logger.debug("* "+hardwareSL['fullyQualifiedDomainName']+" "+username+" "+password)
                    #        logger.debug("* "+softwareComponent['softwareLicense']['softwareDescription']['longDescription'])
                    if ('softwareLicense' in softwareComponent and softwareComponent['softwareLicense']['softwareDescription']['manufacturer'] == 'R1Soft'):
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
                
                mgt_users = []
                if (len(hardwareSL['remoteManagementAccounts'])<>0):
                    for acct in hardwareSL['remoteManagementAccounts']:
                        username = acct['username']
                        password = acct['password']
                        mgt_users.append({username: password})
                deviceSL['mgt_users']=mgt_users

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

    logger.debug("Loading NetScaler list from SL...")
    response = requests.get("https://" + USER + ":" + USER_KEY + "@" + SERVER + REST_NETSCALER)
    if (response.status_code == 200):
        logger.debug("NetScaler list received with success!")
        netscalerListSL = json.loads(response.content)
        for netscalerSL in netscalerListSL:
            deviceSL = {}
            deviceSL['type'] = 'Appliance'
            deviceSL['product'] = 'NetScaler'
            deviceSL['id'] = netscalerSL['id']
            deviceSL['fullyQualifiedDomainName'] = netscalerSL['name']
            deviceSL['primaryBackendIpAddress'] = netscalerSL['managementIpAddress']
            deviceSL['users'] = [{netscalerSL['password']['username']: netscalerSL['password']['password']}]
            deviceListSL.append(deviceSL)
    else:
        logger.error('Error loading NetScaler list from SoftLayer. Devices list is out of date!')
        inError = True
        
    logger.debug("Loading Firewall (Fortigate) list from SL...")
    response = requests.get("https://" + USER + ":" + USER_KEY + "@" + SERVER + REST_PUBLIC_VLANS)
    if (response.status_code == 200):
        logger.debug("VLAN list received with success!")
        vlanListSL = json.loads(response.content)
        for vlanSL in vlanListSL:
            vlanSLID = vlanSL['id']
            
            #check if is a dedicated firewall (fortigate)
            REST_PUBLIC_VLAN_CHECK_IS_DEDICATED_WITH_ID = REST_PUBLIC_VLAN_CHECK_IS_DEDICATED.replace('%VLAN_ID%', `vlanSLID`)
            response = requests.get("https://" + USER + ":" + USER_KEY + "@" + SERVER + REST_PUBLIC_VLAN_CHECK_IS_DEDICATED_WITH_ID)
            if (response.status_code == 200):
                logger.debug("Flag received with success!")
                vlanDedicatedFlagSL = json.loads(response.content)
                if (vlanDedicatedFlagSL):
                    #Get firewall ID and primary IP
                    REST_PUBLIC_VLAN_FIREWALL_WITH_ID = REST_PUBLIC_VLAN_FIREWALL.replace('%VLAN_ID%', `vlanSLID`)
                    response = requests.get("https://" + USER + ":" + USER_KEY + "@" + SERVER + REST_PUBLIC_VLAN_FIREWALL_WITH_ID)
                    if (response.status_code == 200):
                        logger.debug("Firewall received with success!")
                        dedicatedFirewallSL = json.loads(response.content)
                        firewallSLID = dedicatedFirewallSL['id']
                        firewallSLPrimaryIpAddress = dedicatedFirewallSL['primaryIpAddress']
                        
                        #Get firewall FQDN
                        REST_PUBLIC_VLAN_FIREWALL_FQDN_WITH_ID = REST_PUBLIC_VLAN_FIREWALL_FQDN.replace('%FIREWALL_ID%', `firewallSLID`)
                        response = requests.get("https://" + USER + ":" + USER_KEY + "@" + SERVER + REST_PUBLIC_VLAN_FIREWALL_FQDN_WITH_ID)
                        if (response.status_code == 200):
                            logger.debug("Firewall FQDN received with success!")
                            firewallSLFQDN = json.loads(response.content)

                            #Get firewall Credentials
                            REST_PUBLIC_VLAN_FIREWALL_CREDENTIALS_WITH_ID = REST_PUBLIC_VLAN_FIREWALL_CREDENTIALS.replace('%FIREWALL_ID%', `firewallSLID`)
                            response = requests.get("https://" + USER + ":" + USER_KEY + "@" + SERVER + REST_PUBLIC_VLAN_FIREWALL_CREDENTIALS_WITH_ID)
                            if (response.status_code == 200):
                                logger.debug("Firewall credentials received with success!")
                                dedicatedFirewallCredentialsSL = json.loads(response.content)
                                firewallSLCredentialsUsername=dedicatedFirewallCredentialsSL['username']
                                firewallSLCredentialsPassword=dedicatedFirewallCredentialsSL['password']
                                #print `firewallSLID`+ " "+ firewallSLPrimaryIpAddress+ " "+ firewallSLFQDN+ " "+firewallSLCredentialsUsername+ " "+firewallSLCredentialsPassword
                                
                                deviceSL = {}
                                deviceSL['type'] = 'Appliance'
                                deviceSL['product'] = 'Fortigate'
                                deviceSL['id'] = firewallSLID
                                deviceSL['fullyQualifiedDomainName'] = firewallSLFQDN
                                deviceSL['primaryBackendIpAddress'] = firewallSLPrimaryIpAddress
                                deviceSL['users'] = [{firewallSLCredentialsUsername: firewallSLCredentialsPassword}]
                                deviceListSL.append(deviceSL) 
                            else:
                                logger.error('Error loading firewall FQDN from SoftLayer. Devices list is out of date!')
                                inError = True
                        
                        else:
                            logger.error('Error loading firewall FQDN from SoftLayer. Devices list is out of date!')
                            inError = True
                    
                    else:
                        logger.error('Error loading firewall from SoftLayer. Devices list is out of date!')
                        inError = True
            
            else:
                logger.error('Error loading dedicated firewall flag from SoftLayer. Devices list is out of date!')
                inError = True
    else:
        logger.error('Error loading VLAN list from SoftLayer. Devices list is out of date!')
        inError = True

    # PATCHED BY RCASTRIL
    #Salva arquivo de configuracoes     
    with open(devicesFile, 'w') as outfile:
        json.dump( json.dumps(deviceListSL) , outfile)

    return
    # PATCH END. CODE BELOW WONT BE EXECUTED

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
                        
                    deviceUp2date['schedules'] = deviceLocal['schedules']
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
                
                #schedule default by product
                if (deviceSL['product']=="Vyatta"):
                    #schedule=[]
                    scheduleItem={}
                    vpn={}
                    vpn['rule']='* * * * *'
                    vpn['enable']='True'
                    scheduleItem['vpn']=vpn
                    cpu={}
                    cpu['rule']='* * * * *'
                    cpu['enable']='False'
                    scheduleItem['cpu']=cpu
                    #schedule.append(scheduleItem)
                    #"schedules": [ {"vpn": {"rule": "* * * * *", "enable": "True"}}, {"cpu": {"rule": "* * * * *", "enable": "False"}} ]
                else:
                    scheduleItem={}
                deviceSL['schedules']=[]
                deviceSL['schedules'].append(scheduleItem)

                deviceUp2dateList.append(deviceSL)
                
        #Salva arquivo de configuracoes     
        with open(devicesFile, 'w') as outfile:
            json.dump( json.dumps(deviceUp2dateList) , outfile)

    return
