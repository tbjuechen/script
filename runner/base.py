from __future__ import annotations

from abc import ABC, abstractmethod
from multiprocessing import Event, Process, Value
from pathlib import Path
from typing import Any

from loguru import logger
import numpy as np

from .connector import Connector
from .player import CVPlayer, Player


class Runner(ABC, Process):
    """Base process for an automation task."""

    name = "base"
    description = "基础任务"

    _IDLE = 0
    _RUNNING = 1
    _PAUSED = 2
    _STOPPED = 3
    _STOPPING = 4
    _STATUS_NAMES = {
        _IDLE: "idle",
        _RUNNING: "running",
        _PAUSED: "paused",
        _STOPPED: "stopped",
        _STOPPING: "stopping",
    }

    def __init__(
        self,
        connection_class: type[Connector],
        connector_args: dict[str, Any] | None = None,
        player: Player | None = None,
        time_interval: float = 1.0,
        show_gui: bool = False,
        log_queue: Any | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        if time_interval < 0:
            raise ValueError("time_interval must be non-negative")

        self.connection_class = connection_class
        self.connector_args = dict(connector_args or {})
        self.player = player or CVPlayer()
        self.time_interval = time_interval
        self.show_gui = show_gui
        self.log_queue = log_queue

        self._status = Value("i", self._IDLE)
        self.pause_event = Event()
        self.stop_event = Event()
        self.pause_event.set()

        self.connection: Connector | None = None
        self.cache_path: Path | None = None
        self.wanted_path: Path | None = None

    @property
    def status(self) -> str:
        return self._STATUS_NAMES[self._status.value]

    def _set_status(self, status: int) -> None:
        self._status.value = status

    def _initialize(self) -> None:
        self.connection = self.connection_class(**self.connector_args)
        project_root = Path(__file__).resolve().parent.parent
        self.cache_path = project_root / "cache" / f"{self.name}-{self.pid}"
        self.cache_path.mkdir(parents=True, exist_ok=True)
        self.wanted_path = project_root / "wanted"
        self.connection.config.screen_shot_path_local = self.cache_path

    @abstractmethod
    def work(self) -> None:
        """Execute one automation cycle."""

    def run(self) -> None:
        gui = None
        log_sink_id = None
        try:
            if self.log_queue is not None:
                log_sink_id = logger.add(
                    lambda message: self.log_queue.put(str(message)),
                    level="DEBUG",
                    colorize=False,
                    format="{time:HH:mm:ss} | {level: <8} | {message}",
                )
            self._initialize()
            assert self.connection is not None
            if not self.connection.connect():
                raise ConnectionError(
                    f"无法连接设备：{self.connector_args.get('host', '127.0.0.1')}:"
                    f"{self.connector_args.get('port', 16384)}"
                )

            if self.show_gui:
                from .gui import GUI

                gui = GUI()
                gui.start()

            self._set_status(self._RUNNING)
            logger.info("任务 {} 已启动", self.name)
            while not self.stop_event.is_set():
                self.pause_event.wait()
                if self.stop_event.is_set():
                    break
                self.work()
                self.stop_event.wait(self.time_interval)
        except KeyboardInterrupt:
            logger.info("任务 {} 收到停止信号", self.name)
        except Exception:
            logger.exception("任务 {} 异常退出", self.name)
            raise
        finally:
            if self.connection is not None:
                self.connection.disconnect()
            if gui is not None:
                gui.stop()
            if log_sink_id is not None:
                logger.remove(log_sink_id)
            self._set_status(self._STOPPED)
            logger.info("任务 {} 已停止", self.name)

    def pause(self) -> None:
        if self.status != "running":
            raise RuntimeError(f"任务 {self.name} 当前状态不是 running")
        self._set_status(self._PAUSED)
        self.pause_event.clear()

    def resume(self) -> None:
        if self.status != "paused":
            raise RuntimeError(f"任务 {self.name} 当前状态不是 paused")
        self._set_status(self._RUNNING)
        self.pause_event.set()

    def stop(self) -> None:
        self._set_status(self._STOPPING)
        self.stop_event.set()
        self.pause_event.set()

    def screenshot(self) -> str:
        if self.connection is None:
            raise RuntimeError("连接器尚未初始化")
        path = self.connection.screen_shot()
        if not path:
            raise RuntimeError("设备截屏失败")
        return path

    def find(self, target: str, screenshot: str) -> tuple[int, int] | None:
        if self.wanted_path is None:
            raise RuntimeError("任务尚未初始化")
        location = self.player.locate(str(self.wanted_path / target), screenshot)
        if location is not None:
            logger.info("识别到 {}，位置 {}", target, location)
        return location

    def touch(self, x: int, y: int) -> bool:
        if self.connection is None:
            raise RuntimeError("连接器尚未初始化")
        return self.connection.touch(x, y)

    @staticmethod
    def randomize_position(x: int, y: int, offset: int = 10) -> tuple[int, int]:
        return int(x + offset * np.random.normal()), int(y + offset * np.random.normal())

    def find_and_touch(self, target: str, screenshot: str) -> bool:
        location = self.find(target, screenshot)
        if location is None:
            return False
        return self.touch(*self.randomize_position(*location))


class FindListRunner(Runner):
    """Find and touch the first visible target in a list."""

    name = "find-list"
    description = "模板列表任务"
    targets: tuple[str, ...] = ()

    def work(self) -> None:
        screenshot = self.screenshot()
        for target in self.targets:
            if self.find_and_touch(target, screenshot):
                break
