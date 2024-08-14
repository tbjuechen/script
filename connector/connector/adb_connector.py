'''
Author: tbjuechen
Date: 2024-08-12
Version: 1.0
Description: This is a connector with adb-shell, which is used to connect to the android device.
License: MIT
'''

from logging import Logger
from typing import Union
import os
import random

from .base import BaseConnector, BaseConnectorConfig, DefaultConnectorConfig

from adb_shell.adb_device import AdbDeviceTcp

class AdbConnector(AdbDeviceTcp, BaseConnector):
    '''
    A class with methods for connecting to a device via TCP and executing ADB commands base on AdbDeviceTcp.

    Parameters
    ----------
    host : str
        The address of the device; may be an IP address or a host name
    port : int
        The device port to which we are connecting (default is 5555)
    logger : Logger
        The logger object for logging messages
    config : BaseConnector
        The configuration of the connector
    default_transport_timeout_s : float, None
        Default timeout in seconds for TCP packets, or ``None``
    banner : str, bytes, None
        The hostname of the machine where the Python interpreter is currently running; if
        it is not provided, it will be determined via ``socket.gethostname()``
    '''
    def __init__(self, 
                 host:str, 
                 port:int, 
                 logger:Logger, 
                 config:BaseConnectorConfig=DefaultConnectorConfig(),
                 **kwargs):
        default_transport_timeout_s = kwargs.get('default_transport_timeout_s', None)
        banner = kwargs.get('banner', None)
        self.host = host
        self.port = port
        super().__init__(host, port, default_transport_timeout_s, banner)

        self.config:BaseConnectorConfig = config
        self.logger:Logger = logger
        logger.debug(f'build adb connector with host: {host}, port: {port}')
    
    def connect(self)->bool:
        '''Connect to the device.

        Returns
        -------
        bool
            True if the connection was successful, False otherwise
        '''
        self.logger.debug(f'try to connect to {self.host}:{self.port}')
        try:
            super().connect()
            self.logger.info(f'connected to {self.host}:{self.port}')
        except Exception as e:
            self.logger.error(type(e).__name__ + ': ' + str(e))
        finally:
            return self._available
        
    def disconnect(self) -> bool:
        '''Disconnect from the device.
        
        Returns
        -------
        bool
            True if the disconnection was successful, False otherwise
        '''
        self.logger.debug(f'try to disconnect from {self.host}:{self.port}')
        try:
            if not self._available:
                return True
            super().close()
            self.logger.info(f'disconnected from {self.host}:{self.port}')
        except Exception as e:
            self.logger.error(type(e).__name__ + ': ' + str(e))
        finally:
            return not self._available
    
    def shell(self, cmd:str)->Union[str, None]:
        '''execute a shell command on the device.
        
        Parameters
        ----------
        cmd : str
            The command to be executed
            
        Returns
        -------
        Union[str, None]
            The output of the command if the command was successful, None otherwise
        '''
        self.logger.debug(f'try to execute shell command: {cmd}')
        try:
            result = super().shell(cmd)
            self.logger.debug(f'executed shell command: {cmd}')
            return result
        except Exception as e:
            self.logger.error(type(e).__name__ + ': ' + str(e))
        
    def screen_shot(self)->Union[str, None]:
        '''Take a screenshot of the device.
        
        Returns
        -------
        str
            Path to the screenshot file if the screenshot was successful, None otherwise
        '''
        self.logger.debug(f'try to take a screenshot of the device')
        target_path = self.config.SCREEN_SHOT_PATH_LOCAL
        screenshot_name = self.config.SCREEN_SHOT_NAME

        # check if the target path exists, if not create it
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        
        try:
            cmd:str = f'screencap -p sdcard/Pictures/{screenshot_name}.jpg'
            response = self.shell(cmd)
            if not response:
                self.logger.debug('Screenshot success')
            else:
                raise RuntimeError('Screenshot failed with response: ' + response)
            
            # pull the screenshot from the device
            screenshot_path:str = os.path.join(target_path, screenshot_name + '.jpg')
            self.pull(f'sdcard/Pictures/{screenshot_name}.jpg', screenshot_path)
            self.logger.info(f'screenshot saved to {screenshot_path}')
            return screenshot_path
        except Exception as e:
            self.logger.error(type(e).__name__ + ': ' + str(e))

    def _generate_positon(self, x:int, y:int)->tuple:
        '''Generate the position based on the offset.
        
        Parameters
        ----------
        x : int
            The x coordinate
        y : int
            The y coordinate
        
        Returns
        -------
        tuple
            The new position
        '''
        offset_x, offset_y = self.config.OFFSET
        return x + random.randint(-offset_x, offset_x), y + random.randint(-offset_y, offset_y)
    
    def touch(self, x:int, y:int)->bool:
        '''Touch the screen at the specified position.
        
        Parameters
        ----------
        x : int
            The x coordinate
        y : int
            The y coordinate
        
        Returns
        -------
        bool
            True if the touch was successful, False otherwise
        '''
        self.logger.debug(f'try to touch the screen at position ({x}, {y})')
        try:
            x, y = self._generate_positon(x, y)
            cmd:str = f'input tap {x} {y}'
            response:str = self.shell(cmd)
            if not response:
                self.logger.info(f'touched the screen at position ({x}, {y})')
                return True
            else:
                raise RuntimeError('Touch failed with response: ' + response)
        except Exception as e:
            self.logger.error(type(e).__name__ + ': ' + str(e))
            return False
    
    def drag(self, x1:int, y1:int, x2:int, y2:int, duration:float)->bool:
        '''Drag the screen from the start position to the end position.
        
        Parameters
        ----------
        x1 : int
            The start x coordinate
        y1 : int
            The start y coordinate
        x2 : int
            The end x coordinate
        y2 : int
            The end y coordinate
        duration : float
            The duration of the drag
        
        Returns
        -------
        bool
            True if the drag was successful, False otherwise
        '''
        self.logger.debug(f'try to drag the screen from ({x1}, {y1}) to ({x2}, {y2})')
        try:
            x1, y1 = self._generate_positon(x1, y1)
            x2, y2 = self._generate_positon(x2, y2)
            cmd:str = f'input swipe {x1} {y1} {x2} {y2} {int(duration * 1000)}'
            response:str = self.shell(cmd)
            if not response:
                self.logger.info(f'dragged the screen from ({x1}, {y1}) to ({x2}, {y2})')
                return True
            else:
                raise RuntimeError('Drag failed with response: ' + response)
        except Exception as e:
            self.logger.error(type(e).__name__ + ': ' + str(e))
            return False