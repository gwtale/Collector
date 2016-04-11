import modules.log.syslog
import os, sys, json
import paramiko

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
    if remotePath is None:
        remotePath = base['sherlockCachePath']
    if remoteFileName is None:
        remoteFileName = str(fileToSend)

    # Vars
    localFilePath = base['cache_path'] + str(fileToSend)
    remoteFilePath = remotePath + remoteFileName
    host = base['sherlockIp']
    paramiko.util.log_to_file('log/sftp.paramiko.log')

    try:
        t = paramiko.Transport((host, 22))
        t.connect(username=base['scp_ssh_id'], password=base['scp_ssh_pwd'])
        # Copy remote file to server
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.put(str(localFilePath), str(remoteFilePath))
        sftp.close()

        return True
    except Exception as detail:
        logger.error('Error sending file: ' + str(detail))
        return False
