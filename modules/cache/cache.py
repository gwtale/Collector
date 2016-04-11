import json, os, sys, re
import modules.log.syslog

# Vars
baseFile = "config/base.json"

# Logger
logger = modules.log.syslog.getLogger(__name__)
logger.info('cache.py loaded.')

# Load base configuration
if os.path.exists(baseFile):
    with open(baseFile) as infile:
        base = json.load(infile)
    logger.info('Base confuguration loaded.')
else:
    logger.error('Not able to retrieve config/base.json')
    sys.exit()


def dump(input_dict):
    cache_path = base['cache_path']
    strDate = input_dict['timestamp']
    strDate = re.sub('[-:]', '', strDate)
    strDate = re.sub(' ', '_', strDate)
    filename = input_dict['table_name'] + "." + strDate + ".json"
    full_path = cache_path + filename
    try:
        os.stat(base['cache_path'])
    except:
        os.mkdir(base['cache_path'])
    try:
        out_file = open(full_path, "w")
        json.dump(input_dict, out_file, indent=4)
        out_file.close()
        logger.info('Dumped to cache: ' + filename)
    except Exception as detail:
        logger.error('Not able to dump data for table ' + input_dict['table_name'] + '. Error details: ' + str(detail))
