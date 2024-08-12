'''
Author: tbjuechen
Date: 2024-08-12
Version: 1.0
Description: Abstract base class for the connector.
License: MIT
'''

from abc import ABC, abstractmethod
import os

class BaseConnector(ABC):
    @abstractmethod
    def connect(self)->bool:...

    @abstractmethod
    def disconnect(self)->bool:...

    @abstractmethod
    def screen_shot(self, target_path:str)->str:...

    @abstractmethod
    def touch(self, x:int, y:int):...

    @abstractmethod
    def drag(self, x1:int, y1:int, x2:int, y2:int, duration:float):...

class BaseConnectorConfig:
    '''Base class for the configuration of the connector.
    
    Attributes
    ----------
    SCREEN_SHOT_PATH_LOCAL : str
        The local path where the screenshot should be stored
    
    SCREEN_SHOT_NAME : str
        The name of the screenshot file
    
    OFFSET : tuple
        The offset for the touch and drag functions
    '''
    def __init__(self, SCREEN_SHOT_PATH_LOCAL:str, SCREEN_SHOT_NAME:str, OFFSET:tuple):
        self.SCREEN_SHOT_PATH_LOCAL:str = SCREEN_SHOT_PATH_LOCAL
        self.SCREEN_SHOT_NAME:str = SCREEN_SHOT_NAME
        self.OFFSET:tuple = OFFSET
        

class DefaultConnectorConfig(BaseConnectorConfig):
    '''Default configuration of the connector.

    Attributes
    ----------
    SCREEN_SHOT_PATH_LOCAL : str
        cache folder in the current working directory
    
    SCREEN_SHOT_NAME : str
        screenshot
    
    OFFSET : tuple
        (10, 10)
    '''
    def __init__(self):
        super().__init__(SCREEN_SHOT_PATH_LOCAL = os.path.join(os.getcwd(), 'cache'), 
                         SCREEN_SHOT_NAME = 'screenshot', 
                         OFFSET = (10, 10))