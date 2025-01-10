'''
Author: tbjuechen
Date: 2024-08-12
Version: 1.0
Description: An ADB connector for the Mumu emulator.
License: MIT
'''

from .adb_connector import AdbConnector

class MumuConnector(AdbConnector):
    name:str = 'Mumu'
    '''Connector for the Mumu emulator.
    
    Attributes
    ----------
    host : str
        The host of the emulator default:`127.0.0.1`
    
    port : int
        The port of the emulator default:`16384`
    '''
    def __init__(self, host:str='127.0.0.1', port:int=16384, **kwargs):
        super().__init__(host, port,**kwargs)