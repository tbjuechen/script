from __future__ import annotations

from typing import Any

from runner import Runner
from runner.connector import AdbConnector, Connector
from runner.player import Player


class Schedule:
    """Create and control multiple task processes."""

    def __init__(self) -> None:
        self.runners: list[Runner] = []

    def create_runner(
        self,
        script: type[Runner],
        host: str,
        port: int,
        player: Player | None = None,
        connection_class: type[Connector] = AdbConnector,
        **runner_args: Any,
    ) -> Runner:
        runner = script(
            connection_class=connection_class,
            connector_args={"host": host, "port": port},
            player=player,
            **runner_args,
        )
        self.runners.append(runner)
        return runner

    def get_runner(self, index: int) -> Runner:
        return self.runners[index]

    def remove_runner(self, runner_or_index: Runner | int) -> Runner:
        if isinstance(runner_or_index, int):
            return self.runners.pop(runner_or_index)
        self.runners.remove(runner_or_index)
        return runner_or_index

    def start_all(self) -> None:
        for runner in self.runners:
            runner.start()

    def stop_all(self, timeout: float = 5.0) -> None:
        for runner in self.runners:
            if runner.is_alive():
                runner.stop()
        for runner in self.runners:
            if runner.is_alive():
                runner.join(timeout=timeout)

    def join_all(self) -> None:
        for runner in self.runners:
            runner.join()
