'''
Author: tbjuechen
Date: 2024-08-15
Version: 1.1
Description: load the img source from remote server
License: MIT
'''

import os
import requests
import hashlib
import warnings
from urllib.parse import urljoin
from logging import getLogger

logger = getLogger('logger')

REMOTE_ROOT = 'https://8.130.141.36:11000/'

def get_file_hash_remote(url:str) -> str:
    '''get the file hash from remote server

    Parameters
    ----------
    file_path : str
        The file path

    Returns
    -------
    str
        The hash value
    '''
    hash_md5 = hashlib.md5()
    warnings.filterwarnings('ignore', module='urllib3')
    response = requests.get(url, stream=True, verify=False)
    for chunk in response.iter_content(chunk_size=4096):
        hash_md5.update(chunk)
    logger.debug(f'Get hash from remote file: {url}, hash: {hash_md5.hexdigest()}')
    return hash_md5.hexdigest()
    
def get_file_remote(url:str, save_path:str) -> None:
    '''get the file from remote server

    Parameters
    ----------
    url : str
        The url of the file
    save_path : str
        The path to save the file

    Returns
    -------
    None
    '''
    warnings.filterwarnings('ignore', module='urllib3')
    response = requests.get(url, stream=True, verify=False)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=4096):
            file.write(chunk)

def get_file_hash_local(file_path:str) -> str:
    '''get the file hash from local file

    Parameters
    ----------
    file_path : str
        The file path

    Returns
    -------
    str
        The hash value
    '''
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            hash_md5.update(chunk)
    logger.debug(f'Get hash from local file: {file_path}, hash: {hash_md5.hexdigest()}')
    return hash_md5.hexdigest()

def check_local_file(file_name:str)->bool:
    '''check if the local file is the same as the remote file

    Parameters
    ----------
    file_name : str
        The file name

    Returns
    -------
    bool
        True if the file is the same, False otherwise
    '''
    remote_url = urljoin(REMOTE_ROOT, urljoin('wanted/',file_name))
    local_path = os.path.join(os.getcwd(), 'wanted', file_name)
    if not os.path.exists(local_path):
        logger.info(f'File {file_name} does not exist, downloading...')
        get_file_remote(remote_url, local_path)
        return False
    if get_file_hash_remote(remote_url) == get_file_hash_local(local_path):
        logger.debug(f'File {file_name} is the same as the remote file')
        return True
    else:
        logger.info(f'File {file_name} is not the same as the remote file, downloading...')
        get_file_remote(remote_url, local_path)
        return False

def check_remote_version():
    '''check the remote version of the wanted files

    Returns
    -------
    bool
        the version on the remote server
    '''
    remote_url = urljoin(REMOTE_ROOT, 'metadata.json')
    warnings.filterwarnings('ignore', module='urllib3')
    response = requests.get(remote_url, verify=False)
    remote_metadata = response.json()
    return remote_metadata['version']