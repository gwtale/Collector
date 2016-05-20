"""
Created on Mar 31, 2016

@author: jpmenega
"""
import logging, os
from logging.handlers import TimedRotatingFileHandler

def getLogger(module):
    # logging.basicConfig(filename='log/colector.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # logger = logging.getLogger(module)
    logName = 'log/colector.log'
    logger = logging.getLogger(module)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create log dir if it does not exist:
    if not os.path.exists('log/'):
        os.makedirs('log')
        
    # File Handler
    fh = TimedRotatingFileHandler(logName,
                                       when="d",
                                       interval=1,
                                       backupCount=10)
    #fh = logging.FileHandler(logName)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console Handler
    #ch = logging.StreamHandler()
    #ch.setLevel(logging.DEBUG)
    #ch.setFormatter(formatter)
    #logger.addHandler(ch)

    return logger

