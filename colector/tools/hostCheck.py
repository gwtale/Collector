import os
import colector.log.syslog

# Logger
logger = colector.log.syslog.getLogger(__name__)
logger.info('hostCheck.py loaded.')


def ping(address):
    try:
        response = os.system("ping -c 1 -w2 " + address + " > /dev/null 2>&1")
        if response == 0:
            logger.info(address + ' reachable.')
            return 0
        else:
            logger.info(address + ' unreachable.')
            return 1
    except Exception as detail:
        logger.error('Not able to spawn ping process. Error details: ' + str(detail))
