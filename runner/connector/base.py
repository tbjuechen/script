from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


class Connector(ABC):
    """Interface used by runners to control an Android device."""

    @abstractmethod
    def connect(self) -> bool: ...

    @abstractmethod
    def disconnect(self) -> bool: ...

    @abstractmethod
    def screen_shot(self) -> str | None: ...

    @abstractmethod
    def touch(self, x: int, y: int) -> bool: ...

    @abstractmethod
    def drag(self, x1: int, y1: int, x2: int, y2: int, duration: float) -> bool: ...


@dataclass
class ConnectorConfig:
    screen_shot_path_local: Path = field(default_factory=lambda: Path.cwd() / "cache")
    screen_shot_name: str = "screenshot"


BaseConnectorConfig = ConnectorConfig
DefaultConnectorConfig = ConnectorConfig
