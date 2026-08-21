from __future__ import annotations

from dataclasses import dataclass
from multiprocessing import Queue
from pathlib import Path
from queue import Empty
import subprocess
import sys
from threading import Thread
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from runner.connector import ConnectorConfig, MumuConnector
from runner.player import CVPlayer
from runner.simple import Active, Fire, HeroExp, Mitama, Spirit


TASK_CLASSES = (Active, Mitama, HeroExp, Spirit, Fire)
TASKS = {task.name: task for task in TASK_CLASSES}
TASK_LABELS = {f"{task.description}（{task.name}）": task.name for task in TASK_CLASSES}
PROJECT_ROOT = Path(__file__).resolve().parent
BLACK_SCREEN_SCRIPT = PROJECT_ROOT / "black_screen.pyw"


@dataclass(frozen=True)
class Settings:
    task: str
    host: str
    port: int
    threshold: float
    interval: float


def validate_settings(
    task: str, host: str, port: str, threshold: str, interval: str
) -> Settings:
    host = host.strip()
    task_name = TASK_LABELS.get(task, task)
    if task_name not in TASKS:
        raise ValueError("请选择有效任务")
    if not host:
        raise ValueError("ADB 地址不能为空")
    try:
        parsed_port = int(port)
    except ValueError as error:
        raise ValueError("ADB 端口必须是整数") from error
    if not 1 <= parsed_port <= 65535:
        raise ValueError("ADB 端口必须在 1～65535 之间")
    try:
        parsed_threshold = float(threshold)
        parsed_interval = float(interval)
    except ValueError as error:
        raise ValueError("匹配阈值和轮询间隔必须是数字") from error
    if not 0 <= parsed_threshold <= 1:
        raise ValueError("匹配阈值必须在 0～1 之间")
    if parsed_interval < 0:
        raise ValueError("轮询间隔不能小于 0")
    return Settings(task_name, host, parsed_port, parsed_threshold, parsed_interval)


class AutomationApp:
    BG = "#f4f6f9"
    PANEL = "#ffffff"
    TEXT = "#172033"
    MUTED = "#667085"
    PRIMARY = "#4f46e5"
    SUCCESS = "#15803d"
    DANGER = "#b42318"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("阴阳师自动化助手")
        self.root.geometry("1040x780")
        self.root.minsize(900, 700)
        self.root.configure(bg=self.BG)

        self.runner = None
        self.log_queue: Queue[Any] = Queue()
        self.preview_image: tk.PhotoImage | None = None
        self.black_screen_process: subprocess.Popen | None = None
        self.closing = False

        self.task_var = tk.StringVar(value=next(iter(TASK_LABELS)))
        self.host_var = tk.StringVar(value="127.0.0.1")
        self.port_var = tk.StringVar(value="16384")
        self.threshold_var = tk.StringVar(value="0.80")
        self.interval_var = tk.StringVar(value="1.0")
        self.status_var = tk.StringVar(value="未运行")
        self.device_var = tk.StringVar(value="尚未检测模拟器")

        self._configure_style()
        self._build_ui()
        self._set_controls("idle")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(100, self._poll)

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("TFrame", background=self.BG)
        style.configure("Panel.TFrame", background=self.PANEL)
        style.configure("TLabel", background=self.PANEL, foreground=self.TEXT)
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 20, "bold"))
        style.configure("Subtitle.TLabel", foreground=self.MUTED)
        style.configure("Section.TLabel", font=("Microsoft YaHei UI", 11, "bold"))
        style.configure("Status.TLabel", font=("Microsoft YaHei UI", 10, "bold"))
        style.configure("Primary.TButton", font=("Microsoft YaHei UI", 10, "bold"))
        style.configure("TButton", padding=(14, 7))
        style.configure("TEntry", padding=6)
        style.configure("TCombobox", padding=5)

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=20)
        outer.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(outer, style="Panel.TFrame", padding=(22, 18))
        header.pack(fill=tk.X, pady=(0, 14))
        ttk.Label(header, text="阴阳师自动化助手", style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(
            header,
            text="ADB 设备检测 · OpenCV 视觉识别 · 安全启停",
            style="Subtitle.TLabel",
        ).pack(anchor=tk.W, pady=(4, 0))

        body = ttk.Frame(outer)
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(0, weight=0, minsize=330)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        controls = ttk.Frame(body, style="Panel.TFrame", padding=20)
        controls.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        preview = ttk.Frame(body, style="Panel.TFrame", padding=20)
        preview.grid(row=0, column=1, sticky="nsew")
        preview.rowconfigure(2, weight=1)
        preview.columnconfigure(0, weight=1)

        ttk.Label(controls, text="运行配置", style="Section.TLabel").pack(anchor=tk.W)
        self._field(controls, "任务", self._task_combo(controls))
        self._field(controls, "ADB 地址", ttk.Entry(controls, textvariable=self.host_var))
        self._field(controls, "ADB 端口", ttk.Entry(controls, textvariable=self.port_var))

        row = ttk.Frame(controls, style="Panel.TFrame")
        row.pack(fill=tk.X, pady=(0, 12))
        left = ttk.Frame(row, style="Panel.TFrame")
        right = ttk.Frame(row, style="Panel.TFrame")
        left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        right.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
        ttk.Label(left, text="匹配阈值", style="Subtitle.TLabel").pack(anchor=tk.W)
        ttk.Entry(left, textvariable=self.threshold_var).pack(fill=tk.X, pady=(5, 0))
        ttk.Label(right, text="轮询间隔（秒）", style="Subtitle.TLabel").pack(anchor=tk.W)
        ttk.Entry(right, textvariable=self.interval_var).pack(fill=tk.X, pady=(5, 0))

        self.test_button = ttk.Button(controls, text="检测设备并截图", command=self.test_device)
        self.test_button.pack(fill=tk.X, pady=(4, 14))

        separator = ttk.Separator(controls)
        separator.pack(fill=tk.X, pady=(0, 14))

        status_row = ttk.Frame(controls, style="Panel.TFrame")
        status_row.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(status_row, text="任务状态", style="Subtitle.TLabel").pack(side=tk.LEFT)
        self.status_label = ttk.Label(
            status_row, textvariable=self.status_var, style="Status.TLabel"
        )
        self.status_label.pack(side=tk.RIGHT)

        self.start_button = ttk.Button(
            controls, text="启动任务", command=self.start, style="Primary.TButton"
        )
        self.start_button.pack(fill=tk.X, pady=(0, 8))
        action_row = ttk.Frame(controls, style="Panel.TFrame")
        action_row.pack(fill=tk.X)
        self.pause_button = ttk.Button(action_row, text="暂停", command=self.pause)
        self.pause_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self.resume_button = ttk.Button(action_row, text="继续", command=self.resume)
        self.resume_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.stop_button = ttk.Button(action_row, text="停止", command=self.stop)
        self.stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

        self.black_screen_button = ttk.Button(
            controls, text="开启纯黑遮罩", command=self.toggle_black_screen
        )
        self.black_screen_button.pack(fill=tk.X, pady=(12, 0))

        ttk.Label(preview, text="设备画面", style="Section.TLabel").grid(
            row=0, column=0, sticky=tk.W
        )
        ttk.Label(preview, textvariable=self.device_var, style="Subtitle.TLabel").grid(
            row=1, column=0, sticky=tk.W, pady=(4, 12)
        )
        self.preview_label = ttk.Label(
            preview, text="点击“检测设备并截图”查看模拟器画面", anchor=tk.CENTER
        )
        self.preview_label.grid(row=2, column=0, sticky="nsew")

        ttk.Label(preview, text="运行日志", style="Section.TLabel").grid(
            row=3, column=0, sticky=tk.W, pady=(16, 8)
        )
        log_frame = ttk.Frame(preview, style="Panel.TFrame")
        log_frame.grid(row=4, column=0, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        self.log_text = tk.Text(
            log_frame,
            height=9,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg="#101828",
            fg="#d0d5dd",
            insertbackground="white",
            relief=tk.FLAT,
            padx=10,
            pady=8,
            font=("Consolas", 9),
        )
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _task_combo(self, parent: ttk.Frame) -> ttk.Combobox:
        combo = ttk.Combobox(
            parent,
            textvariable=self.task_var,
            values=tuple(TASK_LABELS),
            state="readonly",
        )
        return combo

    @staticmethod
    def _field(parent: ttk.Frame, label: str, widget: ttk.Widget) -> None:
        ttk.Label(parent, text=label, style="Subtitle.TLabel").pack(
            anchor=tk.W, pady=(14, 0)
        )
        widget.pack(fill=tk.X, pady=(5, 0))

    def _settings(self) -> Settings | None:
        try:
            return validate_settings(
                self.task_var.get(),
                self.host_var.get(),
                self.port_var.get(),
                self.threshold_var.get(),
                self.interval_var.get(),
            )
        except ValueError as error:
            messagebox.showerror("配置错误", str(error), parent=self.root)
            return None

    def _append_log(self, message: str) -> None:
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message.rstrip() + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _set_controls(self, state: str) -> None:
        running = state in {"running", "paused", "stopping"}
        self.start_button.config(state=tk.DISABLED if running else tk.NORMAL)
        self.test_button.config(state=tk.DISABLED if running else tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL if state == "running" else tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL if state == "paused" else tk.DISABLED)
        self.stop_button.config(
            state=tk.NORMAL if state in {"running", "paused"} else tk.DISABLED
        )
        labels = {
            "idle": "未运行",
            "running": "运行中",
            "paused": "已暂停",
            "stopped": "已停止",
            "stopping": "正在停止",
            "failed": "异常退出",
        }
        self.status_var.set(labels.get(state, state))

    def test_device(self) -> None:
        settings = self._settings()
        if settings is None:
            return
        self.test_button.config(state=tk.DISABLED)
        self.device_var.set("正在连接设备……")
        self._append_log(f"正在检测 {settings.host}:{settings.port}")

        def worker() -> None:
            config = ConnectorConfig(
                screen_shot_path_local=PROJECT_ROOT / "cache" / "connection-test",
                screen_shot_name="device-preview",
            )
            connector = MumuConnector(
                host=settings.host, port=settings.port, config=config
            )
            try:
                if not connector.connect():
                    raise ConnectionError("ADB 连接失败")
                size = (connector.shell("wm size") or "").strip()
                model = (connector.shell("getprop ro.product.model") or "").strip()
                screenshot = connector.screen_shot()
                if not screenshot:
                    raise RuntimeError("截屏失败")
                self.root.after(0, self._device_test_ok, model, size, screenshot)
            except Exception as error:
                self.root.after(0, self._device_test_failed, str(error))
            finally:
                connector.disconnect()

        Thread(target=worker, daemon=True).start()

    def _device_test_ok(self, model: str, size: str, screenshot: str) -> None:
        self.test_button.config(state=tk.NORMAL)
        try:
            image = tk.PhotoImage(file=screenshot)
            screenshot_size = f"截图 {image.width()}×{image.height()}"
            summary = " · ".join(
                part for part in (model, screenshot_size, size) if part
            )
            self.device_var.set(summary)
            self._append_log(f"设备检测成功：{summary}")
            factor = max(1, (image.width() + 639) // 640, (image.height() + 359) // 360)
            self.preview_image = image.subsample(factor, factor)
            self.preview_label.config(image=self.preview_image, text="")
        except tk.TclError as error:
            summary = " · ".join(part for part in (model, size) if part) or "ADB 已连接"
            self.device_var.set(summary)
            self._append_log(f"设备检测成功：{summary}")
            self._append_log(f"截图预览失败：{error}")

    def _device_test_failed(self, error: str) -> None:
        self.test_button.config(state=tk.NORMAL)
        self.device_var.set("设备检测失败")
        self._append_log(f"设备检测失败：{error}")
        messagebox.showerror("设备检测失败", error, parent=self.root)

    def start(self) -> None:
        settings = self._settings()
        if settings is None:
            return
        task_class = TASKS[settings.task]
        self.runner = task_class(
            connection_class=MumuConnector,
            connector_args={"host": settings.host, "port": settings.port},
            player=CVPlayer(acc=settings.threshold),
            time_interval=settings.interval,
            log_queue=self.log_queue,
        )
        self.runner.start()
        self._set_controls("running")
        self._append_log(f"已启动：{task_class.description}")

    def pause(self) -> None:
        if self.runner is not None and self.runner.is_alive():
            self.runner.pause()
            self._set_controls("paused")
            self._append_log("任务已暂停")

    def resume(self) -> None:
        if self.runner is not None and self.runner.is_alive():
            self.runner.resume()
            self._set_controls("running")
            self._append_log("任务已继续")

    def stop(self) -> None:
        if self.runner is not None and self.runner.is_alive():
            self.runner.stop()
            self._append_log("正在停止任务……")

    def toggle_black_screen(self) -> None:
        if (
            self.black_screen_process is not None
            and self.black_screen_process.poll() is None
        ):
            self._close_black_screen()
            return

        try:
            self.black_screen_process = subprocess.Popen(
                [sys.executable, str(BLACK_SCREEN_SCRIPT)],
                cwd=PROJECT_ROOT,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except OSError as error:
            self._append_log(f"无法开启纯黑遮罩：{error}")
            messagebox.showerror("开启黑屏失败", str(error), parent=self.root)
            return
        self.black_screen_button.config(text="关闭纯黑遮罩（Esc）")
        self._append_log("纯黑遮罩已开启；按 Esc 或 Alt+F4 可退出")

    def _close_black_screen(self) -> None:
        if (
            self.black_screen_process is not None
            and self.black_screen_process.poll() is None
        ):
            self.black_screen_process.terminate()
        self.black_screen_process = None
        self.black_screen_button.config(text="开启纯黑遮罩")
        self._append_log("纯黑遮罩已关闭")

    def _sync_black_screen(self) -> None:
        if (
            self.black_screen_process is not None
            and self.black_screen_process.poll() is not None
        ):
            self.black_screen_process = None
            self.black_screen_button.config(text="开启纯黑遮罩")
            self._append_log("纯黑遮罩已退出")

    def _poll(self) -> None:
        try:
            while True:
                self._append_log(self.log_queue.get_nowait())
        except Empty:
            pass

        if self.runner is not None:
            if self.runner.is_alive():
                self._set_controls(self.runner.status)
            elif self.runner.exitcode is not None:
                state = "stopped" if self.runner.exitcode == 0 else "failed"
                self._set_controls(state)

        self._sync_black_screen()

        if not self.closing:
            self.root.after(100, self._poll)

    def close(self) -> None:
        self.closing = True
        self._close_black_screen()
        if self.runner is not None and self.runner.is_alive():
            self.runner.stop()
            self._wait_for_close(0)
        else:
            self.root.destroy()

    def _wait_for_close(self, attempts: int) -> None:
        assert self.runner is not None
        if not self.runner.is_alive():
            self.root.destroy()
            return
        if attempts >= 30:
            self.runner.terminate()
            self.runner.join(timeout=1)
            self.root.destroy()
            return
        self.root.after(100, self._wait_for_close, attempts + 1)


def main() -> None:
    root = tk.Tk()
    AutomationApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
