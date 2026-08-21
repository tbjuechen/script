from __future__ import annotations

import argparse
from collections.abc import Sequence
import sys

from loguru import logger

from runner.connector import MumuConnector
from runner.player import CVPlayer
from runner.simple import Active, Fire, HeroExp, Mitama, Spirit


TASKS = {
    task.name: task
    for task in (Active, Mitama, HeroExp, Spirit, Fire)
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="阴阳师视觉自动化脚本")
    parser.add_argument(
        "--task",
        choices=TASKS,
        default="active",
        help="要运行的任务（默认：active）",
    )
    parser.add_argument("--host", default="127.0.0.1", help="ADB 地址")
    parser.add_argument("--port", type=int, default=16384, help="ADB 端口")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.8,
        help="模板匹配阈值，范围 0～1（默认：0.8）",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="识别轮询间隔秒数（默认：1）",
    )
    parser.add_argument("--gui", action="store_true", help="显示独立日志窗口")
    parser.add_argument("--debug", action="store_true", help="输出调试日志")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not 0 <= args.threshold <= 1:
        raise SystemExit("--threshold 必须在 0 到 1 之间")
    if args.interval < 0:
        raise SystemExit("--interval 不能小于 0")

    logger.remove()
    logger.add(sys.stderr, level="DEBUG" if args.debug else "INFO")

    task_class = TASKS[args.task]
    runner = task_class(
        connection_class=MumuConnector,
        connector_args={"host": args.host, "port": args.port},
        player=CVPlayer(acc=args.threshold),
        time_interval=args.interval,
        show_gui=args.gui,
    )

    logger.info("启动任务：{}（{}）", task_class.name, task_class.description)
    runner.start()
    try:
        runner.join()
    except KeyboardInterrupt:
        logger.info("正在停止任务……")
        runner.stop()
        runner.join(timeout=5)
        if runner.is_alive():
            logger.warning("任务未及时退出，正在终止子进程")
            runner.terminate()
            runner.join()
    return runner.exitcode or 0


if __name__ == "__main__":
    raise SystemExit(main())
