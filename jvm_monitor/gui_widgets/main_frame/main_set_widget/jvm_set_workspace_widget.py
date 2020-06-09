import configparser
import logging
import os
from tkinter import *
from tkinter import ttk

CONFIG_FILE = 'Resource_Monitor.conf'


class SetWorkspaceWidget:
    def __init__(self, master):
        self.master = master
        self.result_save_path = StringVar()

        self.prep_frame = LabelFrame(master, text='工作路径设置', width=600)
        self.prep_frame.pack(side=TOP, pady=10, fill=X)
        self.path_entry_frame = Frame(self.prep_frame)
        self.path_entry_frame.pack(side=TOP, fill=X, padx=10, pady=5)

    def create_prepare_widget(self):
        Label(self.path_entry_frame, text='工作路径').pack(side=LEFT, anchor=N)
        self.result_save_path_entry = Entry(self.path_entry_frame, textvariable=self.result_save_path, width=32)
        self.result_save_path_entry.configure(state="readonly")
        self.result_save_path_entry.pack(side=LEFT, fill=X, anchor=N)
        Button(self.path_entry_frame, text='浏览...', width=7, style="blue.TButton", command=self._set_path).pack(
            side=LEFT, anchor=N)

    def _set_path(self):
        if self.result_save_path_entry.get():
            init_path = self.result_save_path.get()
        else:
            init_path = os.getcwd()
        path_ = tkFileDialog.askdirectory(initialdir=init_path)
        if path_:
            self.result_save_path.set(path_)
            self._savePath()

    def _savePath(self):
        syspath = self.result_save_path.get()
        cf = configparser.ConfigParser()
        cf.read(CONFIG_FILE, encoding='utf-8-sig')
        cf.set('PATH', 'workspace', syspath)
        with open(CONFIG_FILE, 'w', encoding='utf-8-sig') as f:
            cf.write(f)
