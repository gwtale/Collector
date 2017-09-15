import modules.log.syslog as syslog
import modules.SLApi.deviceListSL as deviceListSL
import os.path
import json

#Vars
configFile = 'config/slapi-config.json'

#Logger
logger = syslog.getLogger(__name__)
logger.info('Colector started.')

#Load credentials
if (os.path.exists(configFile)):
    with open(configFile) as infile:    
        credentials = json.load(infile)
    logger.info('Starting inventory from customer '+credentials['CUSTOMER'])
    print('Starting inventory from customer '+credentials['CUSTOMER'])
    #Device list inventory
    deviceListSL.updateDeviceListFromSL(credentials)
else:
    print("Error loading SL credentials")
    logger.error("Error loading SL credentials")

#End    
logger.info('Collector finished.')
print('Collector finished')
