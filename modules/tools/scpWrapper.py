import modules.log.syslog
import os, sys, json
from paramiko import SSHClient
from scp import SCPClient

# Vars
baseConfig = "config/base.json"

# Logger
logger = modules.log.syslog.getLogger(__name__)
logger.info('scpWrapper.py loaded.')

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

        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(base['sherlockIp'])

        with SCPClient(ssh.get_transport()) as scp:
            scp.put(localFilePath, remoteFileName)
        return True
    except Exception as detail:
        logger.error('Error sending file: ' + str(detail))
        return False
