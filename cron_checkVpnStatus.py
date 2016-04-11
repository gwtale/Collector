# SETUP:
# Create a crontab entry like:
# 0,5,10,15,20,25,30,35,40,45,50,55 * * * * `cd /var/DashboardSL && python cron_checkVpnStatus.py`

# PRE WORK
import json
import os
import sys
import time

import modules.cache.cache as cache
import modules.log.syslog
import modules.tools.hostCheck as hostCheck
import modules.tools.process as process
import modules.vpn.mgtVpn as mgtVpn

baseFile = "config/base.json"
credentialsFile = "config/credentials.json"

# Logger
logger = modules.log.syslog.getLogger("cron_checkVpnStatus")
logger.info('cron_checkVpnStatus.py loaded.')

# Load base configuration
if os.path.exists(baseFile):
    with open(baseFile) as infile:
        base = json.load(infile)
    logger.info('Base confuguration loaded.')
else:
    logger.error('Not able to retrieve config/base.json')
    sys.exit()

# Load credentials
if os.path.exists(credentialsFile):
    with open(credentialsFile) as infile:
        credentials = json.load(infile)
    logger.info('Credentials loaded.')
else:
    logger.error('Not able to retrieve config/credentials.json')
    sys.exit()

# Vars
table_name = 'mgtVpn_status'
results_dict = {}
vpn_endpoint = base['vpn_endpoint']
pvtApi_endpoint = base['pvtApi_endpoint']
array_vpn_path = base['array_vpn_path']
cache_path = base['cache_path']
mgtVpn_status = 0
pvtApiEndp_status = 0

# MAIN CODE
PID = process.getPid(array_vpn_path)
if PID == "0":
    logger.info('Management VPN not running (no array_vpnc64 process found). Calling modules.mgtVpn.start...')
    mgtVpn.start(credentials['account_vpnID'], credentials['account_vpnPassword'], vpn_endpoint, array_vpn_path)
    # Sleep for 5s before continuing with link verification
    time.sleep(5)
else:
    mgtVpn_status = 1
    logger.info('Management VPN already running (PID#' + PID + ')')

# Check connectivity to api endpoint
pingResult = hostCheck.ping(pvtApi_endpoint)
if pingResult == 0:
    logger.info('SoftLayer private API endpoint is REACHABLE')
    pvtApiEndp_status = 1
else:
    logger.error('SoftLayer private API endpoint is UNREACHABLE. Will restart management VPN and try one more time')
    mgtVpn.stop()
    time.sleep(1)
    mgtVpn.start(credentials['account_vpnID'], credentials['account_vpnPassword'], vpn_endpoint, array_vpn_path)
    time.sleep(4)
    pingResult = hostCheck.ping(pvtApi_endpoint)
    if pingResult == 0:
        logger.info('SoftLayer private API endpoint is now REACHABLE')
        mgtVpn_status = 1
        pvtApiEndp_status = 1
    else:
        logger.error('SoftLayer private API endpoint is really UNREACHABLE')


# Build results dictionary
results_dict['account_id'] = int(base['account_id'])
results_dict['mgtVpn_status'] = mgtVpn_status
results_dict['mgtVpn_error'] = 'not implemented'
results_dict['pvtApiEndp_status'] = pvtApiEndp_status
results_dict['table_name'] = table_name
results_dict['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')

# Write pingResult and timestamp to json for uploading. e.g. cache/mgtVpn_201604051749.json
logger.info('Writing cache file...')
cache.dump(results_dict)

logger.info('cron_checkVpnStatus.py FINISHED.')
