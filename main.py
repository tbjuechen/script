'''
Author: tbjuechen
Date: 2024-08-12
Version: 1.0
Description: main file
License: MIT
'''

from logger import logger

from performer import scripts
from performer.performer import Performer
from _version import __description__

from InquirerPy import inquirer
from InquirerPy.base.control import Choice


print(__description__)
performer:Performer = inquirer.select(
    message="Select a script",
    choices=[Choice(value=script,name=script.description) for script in scripts]
).execute()(logger=logger)

performer.run()


