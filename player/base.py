'''
Author: tbjuechen
Date: 2024-08-12
Version: 1.0
Description: base class for all players
License: MIT
'''

from abc import ABC, abstractmethod

class BasePlayer(ABC):
    '''Base class for all players

    Attributes
    ----------
    acc : float
        The accuracy of the player model
    '''
    def __init__(self, acc:float, **kwargs):
        self.acc = acc

    @abstractmethod
    def locate(self, target:str, screenshot:str, debug:bool=False)->tuple:...

    @abstractmethod
    def load(self, path:str)->bool:...