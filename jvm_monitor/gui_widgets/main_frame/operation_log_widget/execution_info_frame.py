import logging
from tkinter import *
from tkinter import ttk


logger = logging.getLogger('JvmMonitor.GUI')

class ExecutionInfoFrame():
    def __init__(self, master):
        self.master = master
        self.execution_info_frame = ttk.LabelFrame(self.master, text='执行日志')
        self.execution_info_frame.pack(side=TOP, anchor=N, fill=X)

    def create_execution_info_widget(self):
        self.execution_info_text = Text(self.execution_info_frame)
        scroll_bar = ttk.Scrollbar(self.execution_info_frame)
        self.execution_info_text.pack(side=LEFT, fill=BOTH, expand=Y)
        self.execution_info_text.tag_config('red', foreground='red')
        self.execution_info_text.tag_config('black', foreground='black')
        self.execution_info_text.configure(yscrollcommand=scroll_bar.set)
        self.execution_info_text.configure(state='disabled')
        scroll_bar.configure(command=self.execution_info_text.yview)
        scroll_bar.pack(side=LEFT, fill=Y)

    def set_res(self, res, tag=None):
        self.execution_info_text.configure(state='normal')
        if tag:
            self.execution_info_text.insert(END, res, 'red')
        else:
            self.execution_info_text.insert(END, res, 'black')
        self.execution_info_text.see(END)
        self.execution_info_text.configure(state='disabled')

    def del_res(self):
        logger.debug('clear result')
        self.execution_info_text.configure(state='normal')
        self.execution_info_text.delete(0.0, END)
        self.execution_info_text.update_idletasks()
        self.execution_info_text.configure(state='disabled')
