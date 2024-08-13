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
    
    MSG_FORMAT = '%(asctime)s - %(module)s - %(message)s'

    # make sure the log level is in the right color and width
    FORMATS = {
        logging.DEBUG: COLORS['DEBUG'] + '[DEBUG]    ' + RESET + MSG_FORMAT,
        logging.INFO: COLORS['INFO'] + '[INFO]     ' + RESET + MSG_FORMAT,
        logging.WARNING: COLORS['WARNING'] + '[WARNING]  ' + RESET + MSG_FORMAT,
        logging.ERROR: COLORS['ERROR'] + '[ERROR]    ' + RESET + MSG_FORMAT,
        logging.CRITICAL: COLORS['CRITICAL'] + '[CRITICAL] ' + RESET + MSG_FORMAT
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=self.datefmt)
        return formatter.format(record)

# create logger with 'logger'
logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# create formatter with datefmt and add it to the handler
formatter = ColoredFormatter(datefmt='%H:%M:%S')
console_handler.setFormatter(formatter)

# add the handler to the logger
logger.addHandler(console_handler)