'''
Author: tbjuechen
Date: 2024-08-12
Version: 1.0
Description: main file
License: MIT
'''

from logger import logger
import os

from performer import scripts
from performer.performer import Performer
from _version import __description__, __online__

from InquirerPy import inquirer
from InquirerPy.base.control import Choice


print(__description__)
logger.warning('默认使用1920*1080分辨率，如需更改请修改wanted文件夹下的图片')
performer:Performer = inquirer.select(
    message="Select a script",
    choices=[Choice(value=script,name=script.description) for script in scripts]
).execute()(logger=logger, online=__online__)

performer.run()

os.system('pause')