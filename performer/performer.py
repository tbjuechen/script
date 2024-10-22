'''
Author: tbjuechen
Date: 2024-08-13
Version: 1.0
Description: performer class
License: MIT
'''
import os
import time
from logging import Logger
from abc import abstractmethod, ABC
from typing import Type, List

from connector import ConnectorPool
from connector.connector.base import BaseConnector
from player.base import BasePlayer
from player import CVPlayer
from .utils import is_valid_ip
from . import loader

from InquirerPy import inquirer

class Performer(ABC):
    '''Performer class

    Attributes
    ----------
    connect_pool : ConnectorPool
        The connector pool
    
    player : BasePlayer
        The player
    '''
    def __init__(self,
                 logger:Logger, 
                 connCls:Type[ConnectorPool]=ConnectorPool, 
                 playerCls:Type[BasePlayer]=CVPlayer,
                 online:bool=True) -> None:
        self.logger = logger
        self.connect_pool = connCls()
        self.player = playerCls()
        self.online = online
        self.init_env()
        self.init_src()
        self.time_dleta = int(inquirer.text(
            message="Enter the time delta (seconds):",
            default='1',
            validate=lambda x: x.isdecimal() and float(x) >= 0,
            invalid_message='Invalid time delta!!!'
        ).execute())

        # runtime variables
        self.last_operation = None
    
    def init_env(self):
        # set the path
        wanted_path = os.path.join(os.getcwd(), 'wanted')
        os.environ['PATH'] += os.pathsep + wanted_path
        self.logger.debug(f'Add wanted path: {wanted_path}')

    def add_connector(self) -> None:
        '''interact add connector to the pool
        '''
        flag:bool = True  # flag to control the loop
        while flag:
            ConnectorType:str = inquirer.select(
                message="Select a connector type (mumu only for now)",
                choices=['Mumu', 'Nox', 'BlueStacks', 'Others'],
            ).execute()
            ConnectorHost:str = inquirer.text(
                message="Enter the connector host:",
                default='127.0.0.1',
                validate=is_valid_ip,
                invalid_message='Invalid ip address!!!'
            ).execute()
            ConnectorPort:int = inquirer.text(
                message="Enter the connector port:",
                default='16384' if ConnectorType == 'Mumu' else '7777',
                validate=lambda x: x.isdigit() and int(x) in range(65536), 
                invalid_message='Invalid port number!!!'
            ).execute()
            self.connect_pool.add_connector(ConnectorType, ConnectorHost, ConnectorPort).connect()
            flag = inquirer.confirm(
                message='Add another connector?',
                default=False
            ).execute()

    def find_and_touch(self, target_list:List[str], connector:BaseConnector=None) -> None:
        '''Find and touch the target in the screenshot

        Parameters
        ----------
        target_list : List[str]
            The list of target image files

        connector : BaseConnector
            The connector to use, if None, use the current connector
        '''
        # use the current connector from pool
        connector = connector if connector else self.connect_pool.get_current_connector()
        screenshot:str = connector.screen_shot()
        for target in target_list:
            location = self.player.locate(target, screenshot)
            if location:
                self.logger.info(f'Found {target} at {location}')
                connector.touch(*location)
                self.last_operation = Operation('touch')

    @abstractmethod
    def main_step(self):
        '''Main steps for the performer
        '''
        pass

    def run(self) -> None:
        '''Run the script with preset steps
        '''
        self.add_connector()
        while True:
            self.main_step()
            self.logger.debug(f'Sleep for {self.time_dleta} seconds')
            time.sleep(self.time_dleta)
            self.check_endless_loop()

    def init_src(self) -> None:
        '''Init the source
        '''
        self.logger.info('Init the source')
        if 'target_list' in self.__dict__.keys():
            if self.online:
                for target in self.target_list:
                    loader.check_local_file(target)
            self.target_list = [os.path.join(self.img_path, i) for i in self.target_list]

    def check_endless_loop(self) -> None:
        '''Check if the script is in an endless loop
        '''
        if self.last_operation:
            if time.time() - self.last_operation.time > 60:
                self.logger.error('Endless loop detected')
                os.system('pause')
                exit()

class Operation:
    '''Operation class

    Attributes
    ----------
    operation : str
        The operation name
    '''
    def __init__(self, operation:str):
        self.operation = operation
        self.time = time.time()