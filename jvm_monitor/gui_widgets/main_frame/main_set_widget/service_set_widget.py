import configparser
import os
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog

MONITOR_HISTORY_FILE = 'Result_Monitor.conf'
CONFIG_FILE = 'Resource_Monitor.conf'


class ServiceSetWidgets:
    def __init__(self, master):
        self.master = master
        self.ip_list_path_entry_frame = Frame(self.master)
        self.ip_list_path_entry_frame.pack(side=TOP, anchor=W, padx=10)
        self.info_show_frame = Frame(self.master)
        self.info_show_frame.pack(side=TOP)
        self.ip_list_path = StringVar()
        self.ip_info_text = Text(self.info_show_frame, width=58, height=10)
        self.ip_list_path_entry = Entry(self.ip_list_path_entry_frame, textvariable=self.ip_list_path, width=32)

    def create_path_entry_widgets(self):
        Label(self.ip_list_path_entry_frame, text='服务器列表文件').pack(side=LEFT, anchor=N)
        self.ip_list_path_entry.configure(state="readonly")
        self.ip_list_path_entry.pack(side=LEFT, fill=X, anchor=N)
        Button(self.ip_list_path_entry_frame, text='浏览...', width=7, style="blue.TButton", command=self._set_path).pack(
            side=TOP, padx=4, anchor=N)
        self.check_ip_list_path()

    def create_ip_info_show_widgets(self):
        scroll_bar = Scrollbar(self.info_show_frame)
        self.ip_info_text.pack(side=LEFT, expand=Y)
        self.ip_info_text.configure(yscrollcommand=scroll_bar.set)
        scroll_bar.configure(command=self.ip_info_text.yview)
        scroll_bar.pack(side=LEFT, fill=Y)
        self.read_ip_list_file()
        self.ip_info_text.bind("<FocusOut>", self.write_ip_list_file)

    def check_ip_list_path(self):
        if os.path.exists('Resource_Monitor.conf'):
            cf = configparser.ConfigParser()
            cf.read('Resource_Monitor.conf', encoding='utf-8-sig')
            self.ip_list_path.set(cf.get(section='PATH', option='ipListPath'))

    def _set_path(self):
        path_ = filedialog.askopenfilename(title="选择服务器配置文件", filetypes=[('TXT文件', 'txt')])
        if path_:
            self.ip_list_path.set(path_)
            self._savePath()

    def _savePath(self):
        syspath = self.ip_list_path.get()
        cf = configparser.ConfigParser()
        cf.read(CONFIG_FILE, encoding='utf-8-sig')
        cf.set('PATH', 'ipListPath', syspath)
        with open(CONFIG_FILE, 'w', encoding='utf-8-sig') as f:
            cf.write(f)

    def read_ip_list_file(self):
        path = self.ip_list_path.get()
        if path:
            with open(path, 'r', encoding="utf-8") as f:
                content = f.read()
            self.ip_info_text.delete(0.0, END)
            self.ip_info_text.insert(END, content)

    def write_ip_list_file(self, *args):
        content = self.ip_info_text.get(0.0, END).strip()
        path = self.ip_list_path.get()
        if content and path:
            with open(path, 'w', encoding="utf8") as f:
                f.write(content)

    def get_ip_info(self):
        return self.ip_info_text.get(0.0, END)
