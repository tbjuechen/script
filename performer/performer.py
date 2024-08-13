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
from abc import abstractmethod
from typing import Type, List

from connector import ConnectorPool
from connector.connector.base import BaseConnector
from player.base import BasePlayer
from player import CVPlayer
from .utils import is_valid_ip

from InquirerPy import inquirer

class Performer:
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
                 playerCls:Type[BasePlayer]=CVPlayer) -> None:
        self.logger = logger
        self.connect_pool = connCls()
        self.player = playerCls()
        self.init_env()
        self.time_dleta = int(inquirer.text(
            message="Enter the time delta (seconds):",
            default='1',
            validate=lambda x: x.isdecimal() and float(x) > 0,
            invalid_message='Invalid time delta!!!'
        ).execute())
    
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