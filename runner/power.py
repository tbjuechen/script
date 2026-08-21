from __future__ import annotations

import sys

from loguru import logger


ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002


def keep_awake(enabled: bool) -> bool:
    """Prevent idle sleep/screensaver while an automation task is running."""
    if sys.platform != "win32":
        return False

    import ctypes

    flags = ES_CONTINUOUS
    if enabled:
        flags |= ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    result = ctypes.windll.kernel32.SetThreadExecutionState(flags)
    if result == 0:
        logger.warning("无法更新 Windows 防休眠状态")
        return False
    logger.debug("Windows 防休眠已{}", "启用" if enabled else "解除")
    return True
