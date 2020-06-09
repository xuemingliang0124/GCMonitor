import configparser
from functools import partial as pto
import logging
from tkinter import ttk
from tkinter import *

from jvm_monitor.decorators import *
from publick_class.ip_list import IpList
from publick_class.threads_control import MyThread

logger = logging.getLogger('XMON.prepare_widget')

MONITOR_HISTORY_FILE = 'Result_Monitor.conf'
CONFIG_FILE = 'Resource_Monitor.conf'


class WorkspaceSetWidget():
    def __init__(self, master):
        self.master = master
        self.prep_frame = ttk.Frame(master, width=600)
        self.prep_frame.pack(side=TOP, pady=2, fill=X)
        self.path_entry_frame = ttk.Frame(self.prep_frame)
        self.path_entry_frame.pack(side=TOP, fill=X, padx=10, pady=2)
        self.ip_list_show_widget = ttk.Frame(self.prep_frame)
        self.ip_list_show_widget.pack(side=TOP, pady=2, fill=X)
        self.result_save_path = StringVar()
        self.ip_list = StringVar()

    def check_workspace(self):
        if os.path.exists('Resource_Monitor.conf'):
            cf = configparser.ConfigParser()
            cf.read('Resource_Monitor.conf', encoding='utf-8-sig')
            self.result_save_path.set(cf.get(section='PATH', option='workspace'))

    def create_workspace_set_widgets(self):
        ttk.Label(self.path_entry_frame, text='工作路径').pack(side=LEFT, anchor=N)
        self.result_save_path_entry = ttk.Entry(self.path_entry_frame, textvariable=self.result_save_path, width=32)
        self.result_save_path_entry.configure(state="readonly")
        self.result_save_path_entry.pack(side=LEFT, fill=X, anchor=N)
        ttk.Button(self.path_entry_frame, text='浏览...', width=7, style="blue.TButton", command=self._set_path).pack(
            side=LEFT, anchor=N)
        self.check_workspace()

    # def create_ip_list_button_widget(self):
    #     text = ['生成iplist模板', '编辑iplist.xlsx']
    #     command = ['self._create_file', 'self._open_iplist']
    #     btn = pto(ttk.Button, self.path_entry_frame, width=10)
    #     pck_set = 'side=LEFT, anchor=W, ipadx=20, padx=10'
    #     for i in range(len(text)):
    #         eval('btn(text="%s", command=%s, style="blue.TButton").pack(%s)' % (text[i], command[i], pck_set))

    # def create_ip_list_show_widget(self):
    #     ip_list_show_text = Text(self.ip_list_show_widget)
    #     scroll_bar = ttk.Scrollbar(self.ip_list_show_widget)
    #     ip_list_show_text.pack(side=LEFT)
    #     ip_list_show_text.place(width=400, height=600)
    #     scroll_bar.configure(command=ip_list_show_text.yview)
    #     scroll_bar.pack(side=RIGHT, fill=X)

    def get_workspace_path(self):
        return self.result_save_path.get()

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

    # @syspathcheck
    # def _create_file(self):
    #     logger.debug('iplist init...')
    #     syspath = self.result_save_path.get()
    #     self.iplist_path = os.path.join(syspath, 'iplist.xlsx')
    #     if os.path.exists(self.iplist_path):
    #         if not tkMessageBox.askyesno(title='通知！',
    #                                      message='%s已存在，是否覆盖？'
    #                                              % self.iplist_path):
    #             logger.debug('iplist init cancel')
    #             self.master.del_res()
    #             self.master.set_res('操作取消！\n')
    #             return
    #     logger.debug('iplist init begin')
    #     IpList(self.result_save_path.get(), self.master).file_init()
    #     logger.debug('iplist init finish')

    # @syspathcheck
    # def _open_iplist(self):
    #     iplist_path = os.path.join(self.result_save_path.get(), 'iplist.xlsx')
    #     MyThread(os.system, (iplist_path,), 'open_iplist').start()

    def _upload_nmon(self):
        step = 'UploadNmon'
        self.master._execute_command(step)
