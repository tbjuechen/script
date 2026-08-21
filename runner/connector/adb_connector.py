from __future__ import annotations

from pathlib import Path
from typing import Any

from adb_shell.adb_device import AdbDeviceTcp
from loguru import logger

from .base import Connector, ConnectorConfig


class AdbConnector(AdbDeviceTcp, Connector):
    """TCP ADB connector for screenshots and input events."""

    def __init__(
        self,
        host: str,
        port: int,
        config: ConnectorConfig | None = None,
        **kwargs: Any,
    ) -> None:
        self.host = host
        self.port = port
        self.config = config or ConnectorConfig()
        super().__init__(
            host,
            port,
            kwargs.get("default_transport_timeout_s"),
            kwargs.get("banner"),
        )

    def connect(self) -> bool:
        logger.debug("正在连接 {}:{}", self.host, self.port)
        try:
            super().connect()
        except Exception:
            logger.exception("连接 {}:{} 失败", self.host, self.port)
            return False
        logger.info("已连接 {}:{}", self.host, self.port)
        return bool(self._available)

    def disconnect(self) -> bool:
        if not self._available:
            return True
        try:
            super().close()
        except Exception:
            logger.exception("断开 {}:{} 失败", self.host, self.port)
            return False
        logger.info("已断开 {}:{}", self.host, self.port)
        return True

    def shell(self, cmd: str) -> str | None:
        try:
            return super().shell(cmd)
        except Exception:
            logger.exception("ADB 命令执行失败：{}", cmd)
            return None

    def screen_shot(self) -> str | None:
        target_dir = Path(self.config.screen_shot_path_local)
        target_dir.mkdir(parents=True, exist_ok=True)
        remote_path = f"/sdcard/Pictures/{self.config.screen_shot_name}.png"
        local_path = target_dir / f"{self.config.screen_shot_name}.png"

        try:
            response = self.shell(f"screencap -p {remote_path}")
            if response is None:
                return None
            if response.strip():
                raise RuntimeError(response.strip())
            self.pull(remote_path, str(local_path))
            logger.debug("截屏已保存至 {}", local_path)
            return str(local_path)
        except Exception:
            logger.exception("设备截屏失败")
            return None

    def touch(self, x: int, y: int) -> bool:
        response = self.shell(f"input tap {x} {y}")
        if response is None:
            return False
        if response.strip():
            logger.error("点击失败：{}", response.strip())
            return False
        logger.debug("点击 ({}, {})", x, y)
        return True

    def drag(self, x1: int, y1: int, x2: int, y2: int, duration: float) -> bool:
        duration_ms = max(0, int(duration * 1000))
        response = self.shell(f"input swipe {x1} {y1} {x2} {y2} {duration_ms}")
        if response is None:
            return False
        if response.strip():
            logger.error("滑动失败：{}", response.strip())
            return False
        return True
