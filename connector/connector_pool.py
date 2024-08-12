'''
Author: tbjuechen
Date: 2024-08-12
Version: 1.0
Description: container for all connectors
License: MIT
'''
from logging import getLogger

from .connector.base import BaseConnector
from .connector import MumuConnector

class ConnectorPool:
    '''A pool of connectors.
    '''
    def __init__(self, logger=None):
        self.connectors = []
        self.current_connector_index = 0
        self.logger = logger if logger else getLogger('logger')

    def add_connector(self, name:str, host:str, port:int, **kwargs)->BaseConnector:
        '''Add a connector to the pool.

        Parameters
        ----------
        name : str
            The name of the connector
        host : str
            The host of the connector
        port : int
            The port of the connector
        kwargs : dict
            Additional arguments for the connector

        Returns
        -------
        int
            The index of the connector in the pool, or -1 if the connector could not be added
        '''
        self.logger.debug(f'add connector {name} with host: {host}, port: {port}')

        try:
            # mumu only for now
            if name == 'Mumu':
                connector = MumuConnector(host, port, logger=self.logger, **kwargs)
            else:
                raise ValueError(f'Unknown simulator {name}')
            
            self.connectors.append(connector)
            self.logger.info(f'connector {name}({host}:{port}) added')
            return connector
        except Exception as e:
            self.logger.error(f'Error adding connector {name}: {e}')
            return None
    
    def get_current_connector(self)->BaseConnector:
        '''Get the current connector.

        Returns
        -------
        BaseConnector
            The current connector
        '''
        self.logger.debug(f'get current connector')
        target_connector:BaseConnector = self.connectors[self.current_connector_index]
        self.current_connector_index = (self.current_connector_index + 1) % len(self.connectors)
        return target_connector
        