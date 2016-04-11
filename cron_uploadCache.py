import pymysql, json, os, sys
import modules.log.syslog
import modules.tools.scp as scp

# Vars
baseConfig = "config/base.json"
conn = None
cursor = None

# Logger
logger = modules.log.syslog.getLogger("cron_uploadCache")
logger.info('cron_uploadCache.py started.')

# Load base configuration
if os.path.exists(baseConfig):
    with open(baseConfig) as infile:
        base = json.load(infile)
else:
    logger.error('Not able to retrieve config/base.json')
    sys.exit()

# Check whether there is job to do
cachedCount = len([name for name in os.listdir(base['cache_path'])])
if cachedCount == 0:
    logger.info('No job to do. Exiting...')
    sys.exit()

# There is work
# Loop through EACH cached file
for cache_file in os.listdir(base['cache_path']):
    try:
        # scp to Sherlock
        scp.send(cache_file)
        # Delete uploaded file
        os.remove(base['cache_path'] + cache_file)
        logger.info('Cache file uploaded and deleted from local cache: {0}'.format(str(cache_file)))
    except Exception as detail:
        logger.error('Not able to upload cache file {0}. Error message: {1}'.format(str(cache_file), str(detail)))

