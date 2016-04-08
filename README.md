# Collector

--- SETUP ---

#1 - Add cron jobs:
    0 5 * * * `cd /var/Collector && python cron_retrieveVpnServiceConfig.py`
    0,5,10,15,20,25,30,35,40,45,50,55 * * * * `cd /var/Collector && python cron_checkVpnStatus.py`
    * * * * * `cd /var/Collector && python cron_uploadCache.py`

#2 - Exchange SSH keys with server running Sherlock project
