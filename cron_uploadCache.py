import pymysql, sys
from os import path, listdir, remove
from json import load
import modules.log.syslog
import modules.tools.scpWrapper as scpWrapper

# Vars
baseConfig = "config/base.json"
conn = None
cursor = None

# Logger
logger = modules.log.syslog.getLogger("cron_uploadCache")
logger.info('cron_uploadCache.py started.')

# Load base configuration
if path.exists(baseConfig):
    with open(baseConfig) as infile:
        base = load(infile)
else:
    logger.error('Not able to retrieve config/base.json')
    sys.exit()

# Check whether there is job to do
cachedCount = len([name for name in listdir(base['cache_path'])])
if cachedCount == 0:
    logger.info('No job to do. Exiting...')
    sys.exit()

# There is work
# Loop through EACH cached file
for cache_file in listdir(base['cache_path']):
    try:
        # scp to Sherlock
        result = scpWrapper.send(cache_file)
        # Delete uploaded file
        if result is True:
            remove(base['cache_path'] + cache_file)
            logger.info('Cache file uploaded and deleted from local cache: {0}'.format(str(cache_file)))
    except Exception as detail:
        logger.error('Not able to upload cache file {0}. Error message: {1}'.format(str(cache_file), str(detail)))

