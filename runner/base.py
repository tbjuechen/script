from abc import ABC, abstractmethod
from multiprocessing import Process, Event, Manager
import os
import time
import io

from loguru import logger
import numpy as np

from .connector import Connector
from .player import Player, CVPlayer
from .gui import GUI

class Runner(ABC, Process):
    name:str = 'Base'
    '''Base class for the runner
    '''
    def __init__(self, connection_class:type, connector_args:dict={}, player_class:type=CVPlayer, player_args:dict={}, time_interval:int=1, **kwargs):
        super().__init__(**kwargs)
        self.status = Manager().Value('s', 'idle')
        self.time_interval = time_interval
        self.connection = None
        self.player = None
        self.logger = None
        self.logger_buffer = None

        self.pause_event = Event()
        self.stop_event = Event()
        self.pause_event.set()

        self.connection_class = connection_class
        self.connector_args = connector_args
        self.player_class = player_class
        self.player_args = player_args

    def path_init(self):
        '''initialize the path
        '''
        local_abs_path = os.getcwd()
        self.cache_path = os.path.join(local_abs_path, 'cache', f'{self.connection.name}-cache')
        os.makedirs(self.cache_path, exist_ok=True)
        self.wanted_path = os.path.join(local_abs_path, 'wanted')
        self.connection.config.SCREEN_SHOT_PATH_LOCAL = self.cache_path

    def _init(self):
        '''Initialize the runner
        '''
        self.logger = logger
        self.logger_buffer = io.StringIO()

        self.connection:Connector = self.connection_class(**self.connector_args)
        self.player = self.player_class(**self.player_args)
        self.status.value = 'idle'

        self.path_init()
        self.logger.debug(f'Runner {self.name} initialized')
        self.init_logger()

        self.gui = GUI()

    def init_logger(self):
        '''
        Initialize the logger
        redirect the log to the io buffer
        '''
        self.logger.remove()
        logger.add(self.logger_buffer, level='DEBUG')

    def get_log(self):
        '''Get the log from the buffer
        '''
        log_info = self.logger_buffer.getvalue()
        self.logger_buffer.seek(0)
        self.logger_buffer.truncate()
        return log_info

    @abstractmethod
    def work(self):
        '''The main sequence of the script
        '''
        pass

    def run(self):
        '''The main loop
        '''
        self._init()
        self.gui.start()

        self.status.value = 'running'
        self.logger.info(f'{self.name} started')
        self.connection.connect()
        while not self.stop_event.is_set():
            self.pause_event.wait()  # wait for resume
            self.work()
            time.sleep(self.time_interval)

        self.connection.disconnect()
        self.logger.info(f'{self.name} stopped')
        self.gui.stop()
    
    def pause(self):
        '''Pause the runner
        '''
        if self.status.value == 'running':
            self.status.value = 'paused'
            self.pause_event.clear()
        else:
            raise ValueError(f'Runner {self.name} is not running')
        
    def resume(self):
        '''Resume the runner
        '''
        if self.status.value == 'paused':
            self.status.value = 'running'
            self.pause_event.set()
        else:
            raise ValueError(f'Runner {self.name} is not paused')
    
    def stop(self):
        '''Stop the runner
        '''
        self.status.value = 'stopped'
        self.stop_event.set()

    def _find(self, target:str):
        '''Find the target in the screenshot

        Parameters
        ----------
        target : str
            The target image file name
        '''
        screenshot:str = self.connection.screen_shot()
        location = self.player.locate(os.path.join(self.wanted_path, target), screenshot)
        if location:
            self.logger.info(f'Found {target} at {location}')
            return location
        else:
            self.logger.debug(f'{target} not found')
            return None
    
    def _touch(self, x:int, y:int):
        '''Touch the screen at the location

        Parameters
        ----------
        x : int
            The x coordinate
        y : int
            The y coordinate
        '''
        self.connection.touch(x, y)
        self.logger.debug(f'Touched at {x}, {y}')

    def generate_position_by_normal(self, x:int, y:int, offset:int=10)->tuple:
        '''Generate the position by normal distribution

        Parameters
        ----------
        x : int
            The x coordinate
        y : int
            The y coordinate
        offset : int, optional
            The offset, by default 10
        '''
        return int(x + offset * np.random.normal()), int(y + offset * np.random.normal())

    def find_and_touch(self, target:str):
        '''Find and touch the target

        Parameters
        ----------
        target : str
            The target image file name
        '''
        location = self._find(target)
        if location:
            location = self.generate_position_by_normal(*location)
            self._touch(*location)
            time.sleep(0.05)
            return True
        else:
            return False
            
