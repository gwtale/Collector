import os
import colector.log.syslog

# Vars
vpnConfig = "config/credentials.json"

# Logger
logger = colector.log.syslog.getLogger(__name__)
logger.info('mgtVpn.py loaded.')


def start(vpn_id, vpn_pass, vpn_endpoint, vpn_path):
    # Start the VPN process
    try:
        args = " -n " + vpn_endpoint + " -u " + vpn_id + " -p " + vpn_pass + " &"
        os.system(vpn_path + args)
        logger.info('array_vpnc64 started. Program output is *NOT* monitored through stdout. Errors will be ignored.')
    except Exception as detail:
        logger.error('Not able to start admin VPN: '+str(detail))


def stop():
    try:
        os.system("killall array_vpnc64")
        logger.info('vpn stopped.')
    except Exception as detail:
        logger.error('Not able to stop admin VPN: '+str(detail))

