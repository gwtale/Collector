import modules.log.syslog
import os, sys, json

# Vars
baseConfig = "config/base.json"

# Logger
logger = modules.log.syslog.getLogger(__name__)
logger.info('scp.py loaded.')

# Load base configuration
if os.path.exists(baseConfig):
    with open(baseConfig) as infile:
        base = json.load(infile)
else:
    logger.error('Not able to retrieve config/base.json')
    sys.exit()


# Load base configuration
def send(fileToSend, remotePath=None, remoteFileName=None):
    try:
        if remotePath is None:
            remotePath = base['sherlockCachePath']
        if remoteFileName is None:
            remoteFileName = remotePath
        else:
            remoteFileName = remotePath + remoteFileName
        localFilePath = base['cache_path'] + str(fileToSend)
        os.system("scp " + localFilePath + " " + base['scp_ssh_id'] + "@" + base['sherlockIp'] + ":" + remoteFileName)
        return True
    except Exception as detail:
        logger.error('Error sending file: ' + str(detail))
        return False
