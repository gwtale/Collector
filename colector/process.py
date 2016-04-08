import subprocess, re
import colector.log.syslog

#Logger
logger = colector.log.syslog.getLogger(__name__)
logger.info('process.py loaded.')

#Load base configuration
def getPid(string):
    try:
        ps= subprocess.Popen("ps -ef|grep " + string + "|grep -v grep|awk '{print $2}'", shell=True, stdout=subprocess.PIPE)
        pid = ps.stdout.read()
        ps.stdout.close()
        ps.wait()
        pid = filter(lambda x: not re.match(r'^\s*$', x), pid)
        pid = pid.strip(' \t\n\r')
        if (pid == ""):
            pid = "0"
	    logger.info('Process ' + string  + ' not found.')
	else:
	    logger.info('Process ' + string  + ' running on PID#' + pid)
        return pid
    except Exception as detail:
        logger.error('Not able to spawn ping process. Error details: ' + str(detail))
