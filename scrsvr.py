import sys
import os
import types
import time
import glob
import random
import configparser
import tkinter as tk
from tkinter import messagebox
import win32gui
import win32con
from ctypes.wintypes import HWND

from PIL import Image, ImageTk


def config_name():
    return os.path.join(os.path.expanduser("~"), 'AppData', 'Local', 'scrsvr', 'scrsvr.ini')


def load_settings():
    config = configparser.ConfigParser(delimiters='=')
    config.read(config_name())
    param = types.SimpleNamespace()
    param.set = config.get('config', 'set')
    # default
    param.delay = config.getint('config', 'delay', fallback=10)
    param.order = config.get('config', 'order', fallback='rand')
    # actual
    param.images = config.get(param.set, 'images')
    param.delay = config.getint(param.set, 'delay', fallback=param.delay)
    param.order = config.get(param.set, 'order', fallback=param.order)
    param.index = config.getint(param.set, 'index', fallback=0)
    return config, param


def save_settings(config, param):
    config.set(param.set, 'index', str(param.index))
    with open(config_name(), 'wt') as configfile:
        config.write(configfile)


SCREEN_SAVER_CLOSING_EVENTS = ['<Any-KeyPress>', '<Any-Button>', '<Motion>']
WAITING_TIME_LAP = 5


class App(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.configure(bg='black')
        self.canvas.pack(fill="both", expand=True)

        self.wm_attributes("-topmost", True)
        # self.overrideredirect(0)
        self.config(cursor="none")
        self.started = False
        self.bind("<Visibility>", lambda event: self.start())
        self.bind_all('<Any-KeyPress>', lambda event: self.close())
        self.bind_all('<Any-Button>', lambda event: self.close())
        self.bind_all('<Motion>', lambda event: self.close())

        self.config, self.param = load_settings()
        self.time = time.time()
        pattern = self.param.images
        self.images = []
        for pattern in self.param.images.strip().splitlines():
            self.images.extend(list(glob.glob(pattern, recursive=True)))

    def start(self):
        # <Visibility> is launched two times. Avoid starting two times with a boolean.
        if self.started is False:
            self.started = True
            self.update_screen()

    def close(self, event=None):
        save_settings(self.config, self.param)
        self.destroy()

    def update_screen(self):
        if self.param.order == 'rand':
            self.imagepath = random.choice(self.images)
        else:
            self.param.index = (self.param.index + 1) % len(self.images)
            self.imagepath = self.images[self.param.index]
        self.img = Image.open(self.imagepath)

        window_width = self.winfo_width()
        window_height = self.winfo_height()
        image_width, image_height = self.img.size
        new_width = window_width
        new_height = new_width * image_height / image_width
        if new_height > window_height:
            new_height = window_height
            new_width = new_height * image_width / image_height
        self.img = self.img.resize((int(new_width), int(new_height)), Image.Resampling.LANCZOS)

        self.imgtk = ImageTk.PhotoImage(self.img)
        x = 0
        y = 0
        if new_width < window_width:
            x = (window_width - new_width) // 2
        if new_height < window_height:
            y = (window_height - new_height) // 2
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.imgtk)
        self.after(5000, self.update_screen)


def preview(parent_hwnd):
    """
    Create the screen saver app and attach it to the screen saver windows dialog (with handle
    parent_hwnd given when calling the screen saver with /p argument).
    Reference:
    https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setparent
    Unfortunately, this does not work (screen saver window is not attached to dialog). Perhaps
    because the style is not changed which can be checked by calling again GetWindowLong
    after SetWindowLong.
    """
    app = App(None)
    hwnd = app.winfo_id()
    old_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    new_style = old_style | win32con.WS_CHILD & ~win32con.WS_POPUP
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
    win32gui.SetParent(hwnd, parent_hwnd)
    app.mainloop()


def scrsvr():
    """
    Entry point for installation
    """
    if len(sys.argv) == 2 and sys.argv[1] == '/dialog':
        os.system('control desk.cpl,,@screensaver')
    elif len(sys.argv) == 2 and sys.argv[1] == '/install':
        os.system(f'start install.bat {__file__}')
    elif len(sys.argv) == 2 and sys.argv[1] == '/config':
        os.system(f'notepad {config_name()}')
    else:
        assert 0


def main():
    # https://docs.microsoft.com/en-us/troubleshoot/windows/win32/screen-saver-command-line
    if len(sys.argv) == 1:
        app = App(None)
        app.mainloop()
    elif len(sys.argv) == 2 and sys.argv[1] == '/c':
        # settings
        os.system(f'notepad {config_name()}')
    elif len(sys.argv) == 3 and sys.argv[1] == '/p':
        # preview
        preview(parent_hwnd=int(sys.argv[2]))
    elif len(sys.argv) == 2 and sys.argv[1] == "/s":
        # run
        app = App(None)
        app.attributes('-fullscreen', True)
        app.mainloop()
    else:
        assert 0


if __name__ == "__main__":
    main()
