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
        remoteFileName = ""

    # Vars
    ssh = paramiko.SSHClient()
    localFilePath = base['cache_path'] + str(fileToSend)
    remoteFilePath = remotePath + remoteFileName
    host = base['sherlockIp']

    try:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=base['scp_ssh_id'], password=base['scp_ssh_pwd'])
        # Copy remote file to server
        sftp = ssh.open_sftp()
        sftp.put(localFilePath, remoteFilePath)
        sftp.close()
        ssh.close()

        return True
    except Exception as detail:
        logger.error('Error sending file: ' + str(detail))
        return False
