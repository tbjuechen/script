'''
Author: tbjuechen
Date: 2024-08-12
Version: 1.0
Description: colored logger
License: MIT
'''

import logging

class ColoredFormatter(logging.Formatter):
    # define color for different log levels
    COLORS = {
        'DEBUG': '\033[90m',   # Grey
        'INFO': '\033[94m',    # Blue
        'WARNING': '\033[93m', # Yellow
        'ERROR': '\033[91m',   # Red
        'CRITICAL': '\033[95m' # Magenta
    }
    RESET = '\033[0m'
    
    MSG_FORMAT = lambda t:f'%(asctime)s {t} %(module)s - %(message)s'

    # make sure the log level is in the right color and width
    FORMATS = {
        logging.DEBUG: MSG_FORMAT(COLORS['DEBUG'] + '  [DEBUG]  ' + RESET),
        logging.INFO: MSG_FORMAT(COLORS['INFO'] + '  [INFO]   ' + RESET),
        logging.WARNING: MSG_FORMAT(COLORS['WARNING'] + ' [WARNING] ' + RESET),
        logging.ERROR: MSG_FORMAT(COLORS['ERROR'] + '  [ERROR]  ' + RESET),
        logging.CRITICAL: MSG_FORMAT(COLORS['CRITICAL'] + '[CRITICAL] ' + RESET)
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=self.datefmt)
        return formatter.format(record)

# create logger with 'logger'
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)

# create console handler and set level to debug
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# create formatter with datefmt and add it to the handler
formatter = ColoredFormatter(datefmt='%H:%M:%S')
console_handler.setFormatter(formatter)

# add the handler to the logger
logger.addHandler(console_handler)