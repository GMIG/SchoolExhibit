import logging
import os
import tkinter as tk
from tkinter import ttk
from VLCPlayer import VLCPlayer
import platform

class VLCPlayerTK(tk.Frame, VLCPlayer):
    def __init__(self, tk_instance, geometry: str, vlc_instance):
        tk.Frame.__init__(self, tk_instance)
        VLCPlayer.__init__(self, vlc_instance)
        tk_instance.geometry(geometry)
        self.container_instance = tk_instance
        self.video_panel = ttk.Frame(self.container_instance)
        self.canvas = tk.Canvas(self.video_panel, background='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.video_panel.pack(fill=tk.BOTH, expand=1)
        if platform.system() == 'Linux':
                self.media_player.set_xwindow(self.video_panel.winfo_id())
        elif platform.system() == 'Windows':
                self.media_player.set_hwnd(self.video_panel.winfo_id())
        #self.container_instance.wm_attributes("-topmost", 1)
        self.container_instance.overrideredirect(True)
        self.container_instance.bind('<KeyPress-F5>', lambda e: self.container_instance.wm_attributes("-topmost", 0))
        self.container_instance.bind('<KeyPress-Escape>', lambda e: os._exit(1))


class BaseTkContainer:

    def __init__(self):
        self.tk_instance = tk.Tk()
        self.tk_instance.title("py player")
        self.tk_instance.protocol("WM_DELETE_WINDOW", self.delete_window)
        self.tk_instance.loadtk()
        self.tk_instance.configure(background='black')
        self.theme = ttk.Style()
        self.theme.theme_use("alt")

    def getTopLevel(self):
        return tk.Toplevel()

    def delete_window(self):
        tk_instance = self.tk_instance
        tk_instance.quit()
        tk_instance.destroy()
        os._exit(1)

    def __repr__(self):
        return "Base tk Container"

"""
root = BaseTkContainer()
tksupport.install(root.tk_instance)

s = SerialPort(Prot(), "com3", reactor, baudrate=57600)
player = PyPlayer(root.tk_instance)
player.create_vlc_instance()
root.tk_instance.overrideredirect(True)
#root.tk_instance.wm_attributes('-toolwindow', 'true')
#root.tk_instance.wm_attributes('-fullscreen','true')

reactor.run()
"""
#root.tk_instance.mainloop()
