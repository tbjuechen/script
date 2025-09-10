'''
Author: tbjuechen
Date: 2024-08-12
Version: 1.0
Description: main file
License: MIT
'''

from runner import Runner
from runner.connector import MumuConnector
from runner.player import CVPlayer
from runner.simple import Mitama,Active

from loguru import logger
import pickle


import time

class Test(Runner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def work(self):
        self.logger.info('Test runner working')
        loc = self._find('ok.jpg')
        if loc:
            self.logger.info(f'Found at {loc}')
        self.logger.info('Test runner finished')
    

if __name__ == '__main__':
    test1 = Active(connection_class=MumuConnector, player=CVPlayer())
    # test2 = Mitama(connection_class=MumuConnector, connector_args={'port':'16416'}, player=CVPlayer())
    test1.start()
    # test2.start()
    test1.join()
    # test2.join()

    # test = Test(connection_class=MumuConnector, player=CVPlayer())

