import pymysql, json, os, sys
import colector.log.syslog

#Vars
baseConfig = "config/base.json"

#Logger
logger = colector.log.syslog.getLogger("cron_uploadCache")
logger.info('cron_uploadCache.py started.')

#Load base configuration
if (os.path.exists(baseConfig)):
    with open(baseConfig) as infile:
        base = json.load(infile)
else:
    logger.error('Not able to retrieve config/base.json')
    sys.exit()

#Check whethere there is job to do
cachedCount = len([name for name in os.listdir(base['cache_path'])])# if os.path.isfile(name)])
if cachedCount == 0:
    logger.info('No job to do. Exiting...')
    sys.exit()
#there is work, so connect to DB and start
try:
    conn = pymysql.connect(host=base["dbServerIp"], port=int(base["dbPort"]), user=base["dbId"], passwd=base["dbPass"], db=base["db"], cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    logger.info('Connected to remote MySQL '+str(base["db"])+' on '+str(base["dbServerIp"])+':'+str(base["dbPort"]))
except Exception as detail:
    logger.error('Not able to connect to '+str(base["db"])+' on '+str(base["dbServerIp"])+':'+str(base["dbPort"])+'. Error message: '+str(detail))


#loop through EACH cached file
for cache_file in os.listdir(base['cache_path']):
    try:
	#Load file as object
	with open(base['cache_path'] + cache_file) as infile:
	    jsonObj = json.load(infile)
	    # read table_name
	table_name = jsonObj['table_name']
	# build SQL query
	strQuery = 'INSERT INTO ' + table_name + ' ('
	for key in jsonObj:
	    if not (key == 'table_name'):
	        strQuery = strQuery + key + ','
	strQuery = strQuery[:-1]
	strQuery = strQuery + ') VALUES ('
	for key, value in jsonObj.items():
	    if not (key == 'table_name'):
	        strQuery = strQuery + "'" + str(value) + "',"
	strQuery = strQuery[:-1]
	strQuery = strQuery + ')'
	# dump all fields into DB
	cursor.execute(strQuery)
	# if success, delete file
	os.remove(base['cache_path'] + cache_file)
	logger.info('Contents of ' + str(cache_file) + ' sent to remte DB and deleted from local disk.')
    except Exception as detail:
	logger.error('Not able to upload cache file. Error message: ' + str(detail))

#Close DB connection
conn.commit()
logger.info('Changes committed to remote DB')
conn.close()
