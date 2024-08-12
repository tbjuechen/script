'''
Author: tbjuechen
Date: 2024-08-12
Version: 1.0
Description: main file
License: MIT
'''

from logger import logger

from connector import ConnectorPool
from player import CVPlayer

connect_pool = ConnectorPool(logger)
connect_pool.add_connector('Mumu', '127.0.0.1', 16384).connect()
player = CVPlayer()
while True:
    current_connector = connect_pool.get_current_connector()
    screenshot = current_connector.screen_shot()
    target_list = ['wanted\\refuse.jpg','wanted\\yyh_begin.jpg', 'wanted\\yys_jieshu.jpg', 'wanted\\yys_jixu.jpg']
    for target in target_list:
        location = player.locate(target, screenshot)
        if location:
            logger.info(f'Found {target} at {location}')
            current_connector.touch(*location)

