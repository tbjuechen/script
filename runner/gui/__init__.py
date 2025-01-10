from threading import Thread

import time
from typing import Callable

import tkinter as tk
from tkinter import font
from multiprocessing import current_process

from loguru import logger

class GUI(Thread):
    '''
    GUI for display the log of the runner in another thread
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logger

    def init_gui(self):
        '''Initialize the GUI
        '''
        self.root = tk.Tk()
        self.root.title(f'Runner {current_process().name} Log')
        self.root.geometry('800x600')
        self.text = tk.Text(self.root, font=font.Font(family='Consolas', size=10))
        self.text.pack(expand=True, fill='both')

        class MultiColorTextHandler:
            """
            自定义日志处理类，为 time、level 和 message 设置不同颜色。
            """
            def __init__(self, text_widget:tk.Text):
                self.text_widget:tk.Text = text_widget
                self.text_widget.config(state=tk.DISABLED)

                # 配置颜色
                self.colors:dict = {
                    "time": "blue",
                    "level": {
                        "DEBUG": "gray",
                        "INFO": "green",
                        "WARNING": "orange",
                        "ERROR": "red",
                        "CRITICAL": "purple",
                    },
                    "message": "black",
                }

                # 定义标签样式
                self.text_widget.tag_configure("time", foreground=self.colors["time"])
                for level, color in self.colors["level"].items():
                    self.text_widget.tag_configure(f"level_{level}", foreground=color)
                self.text_widget.tag_configure("message", foreground=self.colors["message"])

            def write(self, record):
                """
                根据日志记录动态应用不同颜色到 time、level 和 message。
                """
                time = record["time"].strftime("%Y-%m-%d %H:%M:%S")
                level = record["level"].name.ljust(8)
                message = record["message"]

                self.text_widget.config(state=tk.NORMAL)

                # 插入 time
                self.text_widget.insert(tk.END, f"{time} ", "time")

                self.text_widget.insert(tk.END, " | ")

                # 插入 level
                self.text_widget.insert(tk.END, f"{level} ", f"level_{level}")

                self.text_widget.insert(tk.END, " | ")

                # 插入 message
                self.text_widget.insert(tk.END, f"{message}\n", "message")

                self.text_widget.yview(tk.END)
                self.text_widget.config(state=tk.DISABLED)

            def flush(self):
                """
                保留兼容性，但不执行具体操作。
                """
                pass
        
        self.text_handler = MultiColorTextHandler(self.text)

        def log_message_sink(message):
            record = message.record  # 获取日志记录
            self.text_handler.write(record)    # 传递记录给自定义处理器

        self.logger.remove()
        self.logger.add(log_message_sink, level='DEBUG')

        self.root.mainloop()
    
    def run(self):
        '''Run the GUI
        '''
        self.init_gui()

    def stop(self):
        '''Stop the GUI
        '''
        self.root.quit()