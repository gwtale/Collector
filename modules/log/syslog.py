"""
Created on Mar 31, 2016

@author: jpmenega
"""
import logging


def getLogger(module):
    # logging.basicConfig(filename='log/colector.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # logger = logging.getLogger(module)

    logger = logging.getLogger(module)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File Handler
    fh = logging.FileHandler('log/colector.log')
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console Handler
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)
    # ch.setFormatter(formatter)
    # logger.addHandler(ch)

    return logger

