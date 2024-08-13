'''
Author: tbjuechen
Date: 2024-08-13
Version: 1.0
Description: utility functions
'''

import re

# is ip address
IP_ADRESS_PATTERN = r'\b(?:(?:2[0-4][0-9]|25[0-5]|1[0-9]{2}|[1-9]?[0-9])\.){3}(?:2[0-4][0-9]|25[0-5]|1[0-9]{2}|[1-9]?[0-9])\b'

def is_valid_ip(ip:str)->bool:
    '''Check if the ip address is valid

    Parameters
    ----------
    ip : str
        The ip address

    Returns
    -------
    bool
        Whether the ip address is valid
    '''
    return bool(re.match(IP_ADRESS_PATTERN, ip))