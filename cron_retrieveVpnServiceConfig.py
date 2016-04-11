import pymysql, json, os, sys
import modules.log.syslog

# Vars
dbConfig = "config/base.json"
conn = None

# Logger
logger = modules.log.syslog.getLogger("cron_retrieveVpnServiceConfig")
logger.info('cron_retrieveVpnServiceConfig.py started.')

# Load base configuration
if os.path.exists(dbConfig):
    with open(dbConfig) as infile:
        base = json.load(infile)
    try:
        # Connect to remote database
        conn = pymysql.connect(host=base["dbServerIp"], port=int(base["dbPort"]), user=base["dbId"],
                               passwd=base["dbPass"], db=base["db"], cursorclass=pymysql.cursors.DictCursor)
        logger.info('Connected to remote MySQL ' + str(base["db"]) + ' on ' + str(base["dbServerIp"]) + ':' + str(
                base["dbPort"]))
    except Exception as detail:
        logger.error(
                'Not able to connect to {0} on {1}:{2}. Error message: {3}'.format(str(base['db']),
                                                                                   str(base['dbServerIp']),
                                                                                   str(base["dbPort"]), str(detail)))
else:
    logger.error('Not able to retrieve config/base.json')
    sys.exit()

# Read DB
with conn.cursor() as cursor:
    sql = "SELECT `account_userID`, `account_passwd`, `account_vpnID`, `account_vpnPassword`  FROM " + \
          "`customer_accounts` WHERE `account_id`=%s"
    cursor.execute(sql, (base["account_id"],))
    result = cursor.fetchone()
    if result is None:
        logger.error(
                "Empty dataset when querying for VPN and API credentials on table customer_accounts for " +
                "account_id={0}".format(str(base["account_id"])))
    else:
        logger.info("VPN and API credentials retrieved successfully.")

# Close DB connection
conn.close()

# Write results to json
try:
    with open("config/credentials.json", 'w') as outfile:
        json.dump(result, outfile)
    logger.info("Account credentials saved to config/credentials.json.")
except IOError as detail:
    logger.error("Not able to write to credentials file (config/credentials.json)!")
    sys.exit()
