'''
Author: tbjuechen
Date: 2024-08-12
Version: 1.0
Description: player with opencv
License: MIT
'''

from logging import getLogger
import time

from .base import BasePlayer

import cv2
import numpy as np

class CVPlayer(BasePlayer):
    '''Player with opencv

    Attributes
    ----------
    acc : float
        The accuracy of the player model (default 0.8)
    '''
    def __init__(self, acc:float=0.8, **kwargs):
        super().__init__(acc, **kwargs)
        self.logger = getLogger('logger')

    def load(self, path:str)->cv2.typing.MatLike:
        '''Load an image from a file

        Parameters
        ----------
        path : str
            The path of the image file

        Returns
        -------
        cv2.typing.MatLike
            The image
        '''
        self.logger.debug(f'load image from {path}')
        try:
            return cv2.imread(path)
        except Exception as e:
            self.logger.error(f'Error loading image from {path}: {e}')
    
    def locate(self, target:str, screenshot:str, debug:bool=False)->tuple:
        '''Locate the target in the screenshot
        
        Parameters
        ----------
        target : str
            The path of the target image file
        screenshot : str
            The path of the screenshot image file
        debug : bool
            Whether to show the debug information (default False)
        '''
        self.logger.debug(f'locate {target} in {screenshot}')

        target_img:cv2.typing.MatLike = self.load(target)
        screenshot_img:cv2.typing.MatLike = self.load(screenshot)

        marks = []  # debug only
        positon:list = []  # result

        target_h, target_w = target_img.shape[:2]  # shape: (height, width, channels)
        result = cv2.matchTemplate(screenshot_img, target_img, cv2.TM_CCOEFF_NORMED)
        location = np.where(result >= self.acc)

        dis = lambda a, b: ((a[0]-b[0])**2 + (a[1]-b[1])**2) **0.5  # distance between two points

        for y, x in zip(*location):
            center: tuple[int,int] = x + int(target_w/2), y + int(target_h/2)
            if positon and dis(positon[-1], center) < 20:  # ignore nearby points
                continue
            else:
                positon.append(center)
                p2: tuple[int,int] = x + target_w, y + target_h
                marks.append(((x, y), p2))
        
        self.logger.info(f'Found {len(positon)} target(s) of {target}')

        if debug:
            self.logger.debug(f'Found {len(positon)} target(s)  ' + ' '.join([f'{i}: {mark}' for i, mark in enumerate(positon)]))
            for i, mark in enumerate(marks):
                screenshot_img = self.mark(screenshot_img, mark[0], mark[1])
            cv2.imshow(f'result for {target}:', screenshot_img)
            cv2.waitKey(0) 
            cv2.destroyAllWindows()

        return positon[0] if positon else None
    
    def mark(self, img:cv2.typing.MatLike, p1:tuple[int,int], p2:tuple[int,int])->None:
        '''Mark a rectangle on the image
        
        Parameters
        ----------
        img : cv2.typing.MatLike
            The image
        p1 : tuple
            The top-left point of the rectangle
        p2 : tuple
            The bottom-right point of the rectangle
        '''
        cv2.rectangle(img, p1, p2, (0, 0, 255), 2)
        return img
    
    def _wait(self, ms:int)->None:
        '''Wait for a while
        
        Parameters
        ----------
        ms : int
            The time to wait in milliseconds
        '''
        self.logger.debug(f'Waiting for {ms} seconds')
        time.sleep(ms / 1000)