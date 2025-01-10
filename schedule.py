from runner import Runner
from runner.connector import Connector, AdbConnector
from runner.player import Player, CVPlayer

from functools import singledispatch
from loguru import logger

class Schedule:
    def __init__(self, config:dict=None):
        self.logger = logger
        self.connectors:list[Connector] = []
        self.runners:list[Runner] = []
    
    def create_connector(self, host:str, port:int, conn=AdbConnector)->Connector:
        '''Create a connector.

        Parameters
        ----------
        host : str
            The host of the connector
        port : int
            The port of the connector
        conn : Connector, optional
            The connector class, by default AdbConnector

        Returns
        -------
        Connector
            The connector
        '''
        connector = conn(host, port)
        self.connectors.append(connector)
        return connector
    
    @singledispatch
    def remove_connector(self, param):
        raise NotImplementedError(f'Unsupported type {type(param)}')
    
    @remove_connector.register(Connector)
    def _(self, connector:Connector):
        '''Remove a connector.

        Parameters
        ----------
        connector : Connector
            The connector to be removed
        '''
        self.connectors.remove(connector)
    
    @remove_connector.register(int)
    def _(self, index:int):
        '''Remove a connector by index.

        Parameters
        ----------
        index : int
            The index of the connector to be removed
        '''
        self.connectors.pop(index)

    def list_connectors(self):
        '''List all connectors.
        '''
        return self.connectors
    
    def remove_all_connectors(self):
        '''Remove all connectors.
        '''
        for connector in self.connectors:
            connector.disconnect()
            self.remove_connector(connector)
    
    def get_connector(self, index:int)->Connector:
        '''Get a connector by index.

        Parameters
        ----------
        index : int
            The index of the connector

        Returns
        -------
        Connector
            The connector
        '''
        return self.connectors[index]
    
    def create_runner(self, connector:Connector, script:object, player:Player = None)->Runner:
        '''Create a runner.

        Parameters
        ----------
        connector : Connector
            The connector to use
        player : Player
            The player to use

        Returns
        -------
        Runner
            The runner
        '''
        if player is None:
            player = CVPlayer()
        
        runner:Runner = script(connector, player)
        self.runners.append(runner)

    def list_runners(self):
        '''List all runners.
        '''
        return self.runners
    
    @singledispatch
    def remove_runner(self, param):
        raise NotImplementedError(f'Unsupported type {type(param)}')
    
    @remove_runner.register(Runner)
    def _(self, runner:Runner):
        '''Remove a runner.

        Parameters
        ----------
        runner : Runner
            The runner to be removed
        '''
        self.runners.remove(runner)

    @remove_runner.register(int)
    def _(self, index:int):
        '''Remove a runner by index.

        Parameters
        ----------
        index : int
            The index of the runner to be removed
        '''
        self.runners.pop(index)

    def get_runner(self, index:int)->Runner:
        '''Get a runner by index.

        Parameters
        ----------
        index : int
            The index of the runner

        Returns
        -------
        Runner
            The runner
        '''
        return self.runners[index]
    
    def begin_runner(self, index:int):
        '''Begin a runner by index.

        Parameters
        ----------
        index : int
            The index of the runner
        '''
        self.runners[index].start()
        