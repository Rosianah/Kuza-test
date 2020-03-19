import tkinter as tk, logging, json, os, telethon.sync, time, difflib, re, traceback, Levenshtein, asyncio
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
from tkinter import Tk, filedialog, Button, Menubutton, Menu, Label, Frame, StringVar, IntVar, Tk, DISABLED, NORMAL, BOTTOM, TOP

import HomeInterface, TelegramInterface, SMSInterface
#This class controls the frames
class SeaOfFrames(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        SMS = SMSInterface

        #dict that holds the frames
        self.frames = {}

        #loop through the frames as well as set the geometry for each frame
        for allframes, geometry in zip ((HomeInterface.HomeInterfaces, TelegramInterface.TelegramInterfaces, SMSInterface.SMSInterfaces), ('650x650', '650x650', '650x650')):
            page_name = allframes.__name__
            frame = allframes(container, self)
            self.frames[page_name] = (frame, geometry)
            frame.grid(row = 0, column = 0, sticky = "nsew")
        
        #first frame to be displayed
        self.show_frame("HomeInterface")

    #the function that shows the frames
    def show_frame(self, page_name):
        frame, geometry = self.frames[page_name]
        self.geometry(geometry)
        frame.tkraise()

app = SeaOfFrames()
app.mainloop()