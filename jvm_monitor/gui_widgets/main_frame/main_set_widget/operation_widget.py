from configparser import ConfigParser
from functools import wraps
from functools import partial as pto
import logging
import os
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import simpledialog

MONITOR_RECORD = 'MonitorRecord.txt'
logger = logging.getLogger("JvmMonito.GUI")


def kill_monitor_confirm(func):
    @wraps(func)
    def wrapped_function(*args):
        if not messagebox.askokcancel(title='警告！', message='警告：此操作将终止监控进程，操作不可逆！是否继续？'):
            args[0].top_master.del_res()
            args[0].top_master.set_res('操作取消！')
        else:
            func(*args)

    return wrapped_function


class OperationWidget:
    def __init__(self, master, top_master):
        self.master = master
        self.top_master = top_master
        self.run_monitor_frame = Frame(self.master)
        self.run_monitor_frame.pack(side=TOP, anchor=W)
        self.monitor_record_frame = Frame(self.master)
        self.monitor_record_frame.pack_forget()
        self.end_monitor_frame = Frame(self.master)
        self.end_monitor_frame.pack(side=TOP, pady=10)

        # self.upgc_widget = Frame(self.run_monitor_frame)
        # self.upgc_widget.pack_forget()

    # def create_operation_widget(self, top_master):
    #     self
    #     self.run_monitor_frame.create_run_monitor_widget()
    #     self.run_monitor_frame.creat_download_history_widget()
    #
    #     self.exe_fr = Frame(master)
    #     self.exe_fr.pack(side=TOP, pady=10, anchor=N, fill=X)

    def create_run_monitor_widget(self):
        text = ['1:环境初始化', '2:启动监控', '3:收集结果并分析']
        command = ['init_monitor', 'run_monitor', 'show_download_widget']
        btn = pto(Button, self.run_monitor_frame, width=10)
        pck_set = 'side=LEFT, anchor=W, ipadx=20, padx=10'
        for i in range(len(text)):
            eval('btn(text=text[i], command=self.%s, style="springgreen.TButton").pack(%s)' % (
                command[i], pck_set))

    def create_end_monitor_widget(self):
        text = ['停止监控', '清理监控']
        command = ['kill_monitor', 'deleteRes']
        colors = ['red', 'green']
        btn = pto(Button, self.end_monitor_frame, width=10)
        pck_set = 'side=LEFT, anchor=W, ipadx=20, padx=10'
        for i in range(len(text)):
            eval('btn(text=text[i], command=self.%s, style="%s.TButton").pack(%s)' % (
                command[i], colors[i], pck_set))

    def create_download_history_widget(self):
        self.monitor_history_download_combobox = Combobox(self.monitor_record_frame, width=50, height=20)
        self.read_monitor_history()
        lens = len(self.monitor_history_download_combobox['values'])
        self.monitor_history_download_combobox.pack(side=TOP, padx=5, pady=5)
        self.monitor_history_download_combobox.current(0)
        self.monitor_history_download_combobox.bind('<<ComboboxSelected>>', self.read_monitor_history)

    def create_clear_local_result_dialog(self):
        Button(self.monitor_record_frame, text='确认下载', style="springgreen.TButton",
               command=self.download_result, width=8).pack(side=LEFT, anchor=W, ipadx=20, padx=10)

        Button(self.monitor_record_frame, text='取消', style="springgreen.TButton",
               command=self.monitor_record_frame.pack_forget, width=8).pack(side=LEFT, anchor=W, ipadx=20, padx=10)

        Button(self.monitor_record_frame, text='清除记录', style="red.TButton",
               command=self.clear_local_monitor_history, width=8).pack(side=LEFT, anchor=W, ipadx=20, padx=10)

    def init_monitor(self):
        step = 'InitEnv'
        self.top_master.execute_command(step)

    def run_monitor(self):
        step = 'runJvmMonitor'
        self.top_master.execute_command(step)

    def download_result(self):
        self.monitor_record_frame.pack_forget()
        download_combobox_selected_value = self.monitor_history_download_combobox.get()
        scene_date = download_combobox_selected_value[6:14]
        scene_time = download_combobox_selected_value[14:18]
        scene_name = download_combobox_selected_value[25:]
        scene_info = {'scene_date': scene_date, 'scene_time': scene_time, 'scene_name': scene_name}
        step = 'DownLoadResult'
        self.top_master.execute_command(step, download_scene_info=scene_info)

    def show_download_widget(self):
        self.monitor_record_frame.pack(side=TOP, anchor=W, padx=20, before=self.end_monitor_frame)

    def hide_download_widget(self):
        self.monitor_record_frame.pack_forget()

    def deleteRes(self):
        self.delete_result(self.top_master)

    def clear_local_monitor_history(self):
        logger.debug('clear_page...')
        conf_path_res = 'Result_Monitor.conf'
        message_text = '此操作将删除本地保存的执行记录,不影响服务器和本地的监控结果,\n所有结果后续可通过自定义下载,建议每次项目完成后清理执行记录.\n是否继续?'
        if messagebox.askokcancel('通知!', message_text):
            os.remove(conf_path_res)
            self.top_master.clear_page()
        self.monitor_record_frame.pack_forget()

    @kill_monitor_confirm
    def kill_monitor(self):
        step = 'killJstat'
        self.top_master.execute_command(step)

    def read_monitor_history(self, *args):
        # logger.debug('read_result...')
        with open(MONITOR_RECORD, 'r', encoding="utf8") as f:
            content = f.readlines()
        if content:
            monitor_records = []
            for monitor_record in content:
                if monitor_record.startswith("请选择"):
                    monitor_records.append(monitor_record)
                    continue
                monitor_record = monitor_record.strip().split(":")
                monitor_record = "场景名称：" + monitor_record[0] + ",开始时间：" + monitor_record[1]
                monitor_records.append(monitor_record)
            self.monitor_history_download_combobox['values'] = monitor_records
            self.monitor_history_download_combobox.current(0)
            self.monitor_history_download_combobox['state'] = 'readonly'

    def delete_result(self, gui):
        if messagebox.askokcancel('警告!', '此操作将永久删除服务器的mon_result文件夹下所有内容，请谨慎操作！\n是否继续？'):
            delete_dialog = simpledialog.askstring(title='确认', prompt='如确认删除，请输入“删除”')
            if delete_dialog == '删除':
                step = 'DeleteResult'
                logger.debug('delete result begin,step:%s' % step)
                self.top_master.execute_command(step)
            else:
                logger.debug('delete result cancel')
                gui.del_res()
                gui.set_res('操作取消！\n')
        else:
            logger.debug('delete result cancel')
            gui.del_res()
            gui.set_res('操作取消！\n')
