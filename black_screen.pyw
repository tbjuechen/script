"""Fullscreen black cover for unattended automation.

Press Escape or Alt+F4 to close it. The automation process and ADB capture keep
running behind this window.
"""

from __future__ import annotations

import tkinter as tk


def main() -> None:
    root = tk.Tk()
    root.title("阴阳师自动化 - 黑屏运行")
    root.configure(background="black")
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.bind("<Escape>", lambda _event: root.destroy())
    root.bind("<Control-Shift-Q>", lambda _event: root.destroy())
    root.mainloop()


if __name__ == "__main__":
    main()
