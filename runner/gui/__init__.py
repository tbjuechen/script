from multiprocessing import current_process
from queue import Empty, Queue
from threading import Event, Thread
import tkinter as tk
from tkinter import font

from loguru import logger


class GUI(Thread):
    """Optional, thread-safe log window for a runner process."""

    def __init__(self) -> None:
        super().__init__(daemon=True)
        self._messages: Queue[str] = Queue()
        self._stop_event = Event()
        self._sink_id: int | None = None

    def run(self) -> None:
        root = tk.Tk()
        root.title(f"Runner {current_process().name} Log")
        root.geometry("800x600")
        text = tk.Text(root, font=font.Font(family="Consolas", size=10), state=tk.DISABLED)
        text.pack(expand=True, fill="both")

        self._sink_id = logger.add(lambda message: self._messages.put(str(message)), level="DEBUG")

        def update() -> None:
            try:
                while True:
                    message = self._messages.get_nowait()
                    text.config(state=tk.NORMAL)
                    text.insert(tk.END, message)
                    text.see(tk.END)
                    text.config(state=tk.DISABLED)
            except Empty:
                pass
            if self._stop_event.is_set():
                root.destroy()
            else:
                root.after(100, update)

        root.after(100, update)
        root.mainloop()
        if self._sink_id is not None:
            logger.remove(self._sink_id)

    def stop(self) -> None:
        self._stop_event.set()
