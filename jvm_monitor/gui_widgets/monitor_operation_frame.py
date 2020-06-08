from configparser import ConfigParser
from functools import partial as pto
from functools import wraps
from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
import logging
import os

logger = logging.getLogger('JvmMonitor.GUI')


def kill_monitor_confirm(func):
    @wraps(func)
    def wrapped_function(*args):
        if not messagebox.askokcancel(title='警告！', message='警告：此操作将终止监控进程，操作不可逆！是否继续？'):
            args[0].top_master.del_res()
            args[0].top_master.set_res('操作取消！')
        else:
            func(*args)

    return wrapped_function


class MonitorOperationFrame():
    def __init__(self, master):
        self.monitor_operation_frame = ttk.LabelFrame(master, text='监控场景设置')
        self.monitor_operation_frame.pack(side=TOP, pady=10, anchor=N, fill=X)

        self.upgc_widget = ttk.Frame(self.monitor_operation_frame)
        self.upgc_widget.pack_forget()

        self.scene_set_sub_frame = SceneSetSubFrame
        self.scene_info = ''

    def create_scene_set_widget(self):
        scene_set_frame = ttk.Frame(self.monitor_operation_frame)
        scene_set_frame.pack(side=TOP, anchor=N, pady=10, fill=X)
        self.scene_set_sub_frame = SceneSetSubFrame(scene_set_frame)
        self.scene_set_sub_frame.create_scene_set_widget()

    def create_monitor_operation_widget(self, top_master):
        self.run_monitor_frame = RunMonitorFrame(self.monitor_operation_frame, top_master)
        self.run_monitor_frame.create_run_monitor_widget()
        self.run_monitor_frame.creat_download_history_widget()

    def get_scene_info(self):
        return self.scene_set_sub_frame.get_scene_info()

    def read_monitor_history(self):
        self.run_monitor_frame.read_monitor_history()

    def hide_download_widget(self):
        self.run_monitor_frame.hide_download_widget()


class SceneSetSubFrame():
    def __init__(self, master):
        self.scene_name_frame = ttk.Frame(master)
        self.scene_name_frame.pack(side=LEFT, anchor=N, padx=5)

        self.scene_step_frame = ttk.Frame(master)
        self.scene_step_frame.pack(side=LEFT, padx=5)

        self.scene_times_frame = ttk.Frame(master)
        self.scene_times_frame.pack(side=LEFT, padx=5)

        self.scene_time_frame = ttk.Frame(master)
        self.scene_time_frame.pack(side=LEFT, padx=5)
        self.scene_name = StringVar()
        self.scene_times = IntVar()
        self.unit = StringVar()
        self.scene_time_list = ['5分钟', '10分钟', '15分钟', '30分钟', '1小时', '8小时', '12小时']
        self.scene_time_second_list = [300, 600, 900, 1800, 3600, 28800, 14400, 43200]
        self.scene_step_list = ['3', '5', '15', '30', '60']

    def create_scene_set_widget(self):
        ttk.Label(self.scene_name_frame, text='场景名称', width=8).pack(side=LEFT, anchor=W)
        ttk.Entry(self.scene_name_frame, text=self.scene_name, width=20).pack(side=LEFT, anchor=W)

        ttk.Label(self.scene_step_frame, text='采集间隔', width=8).pack(side=LEFT, anchor=W)
        self.scene_step_comb = ttk.Combobox(self.scene_step_frame, width=3, state="readonly")
        self.scene_step_comb.pack(side=LEFT, anchor=W)
        self.scene_step_comb['values'] = self.scene_step_list
        self.scene_step_comb.current(0)
        self.scene_step_comb.bind("<<ComboboxSelected>>", self._calculation_monitor_times)
        ttk.Label(self.scene_step_frame, text='秒', width=4).pack(side=LEFT, anchor=W)

        ttk.Label(self.scene_times_frame, text='监控时长', width=8).pack(side=LEFT, anchor=W)
        self.scene_time_comb = ttk.Combobox(self.scene_times_frame, width=6, state="readonly")
        self.scene_time_comb.pack(side=LEFT, anchor=W)
        self.scene_time_comb['values'] = self.scene_time_list
        self.scene_time_comb.current(0)
        self.scene_time_comb.bind("<<ComboboxSelected>>", self._calculation_monitor_times)

        self.unit.set('次')
        ttk.Label(self.scene_time_frame, text='采集次数：', width=8).pack(side=LEFT, anchor=W)
        self.scene_times_label = ttk.Label(self.scene_time_frame, textvariable=self.scene_times, width=1)
        self.scene_times_label.pack(side=LEFT, anchor=W)
        ttk.Label(self.scene_time_frame, textvariable=self.unit, width=4).pack(side=LEFT, anchor=W)
        self._calculation_monitor_times()

    def get_scene_info(self):
        return {'scene_name': self.scene_name.get(), 'scene_step': int(self.scene_step_comb.get()),
                'scene_times': self.scene_times.get()}

    def _calculation_monitor_times(self, *args):
        scene_time = self.scene_time_second_list[self.scene_time_list.index(self.scene_time_comb.get())]
        scene_step = int(self.scene_step_comb.get())
        scene_times = scene_time // scene_step
        width = len('%s' % scene_times)
        self.scene_times.set(scene_times)
        self.scene_times_label.configure(width=width)


class RunMonitorFrame():
    def __init__(self, master, top_master):
        self.top_master = top_master
        self.exe_fr = ttk.Frame(master)
        self.exe_fr.pack(side=TOP, pady=10, anchor=N, fill=X)

        self.download_history_mode_frame = ttk.Frame(master)
        self.download_history_mode_frame.pack_forget()

    def create_run_monitor_widget(self):
        text = ['环境初始化', '启动监控', '下载监控结果并解析', '删除监控结果', '终止监控进程']
        command = ['init_monitor', 'run_monitor', 'show_download_widget', 'deleteRes', 'kill_monitor']
        colors = ['blue', 'green', 'blue', 'red', 'red']
        btn = pto(ttk.Button, self.exe_fr, width=10)
        pck_set = 'side=LEFT, anchor=W, ipadx=20, padx=10'
        for i in range(len(text)):
            eval('btn(text=text[i], command=self.%s, style="%s.TButton").pack(%s)' % (
                command[i], colors[i], pck_set))

    def creat_download_history_widget(self):
        self.monitor_history_download_combobox = ttk.Combobox(self.download_history_mode_frame, width=60, height=20)
        self.read_monitor_history()
        lens = len(self.monitor_history_download_combobox['values'])
        self.monitor_history_download_combobox.pack(side=TOP, padx=5, pady=5)
        self.create_clear_local_result_dialog()
        self.monitor_history_download_combobox.current(0)
        self.monitor_history_download_combobox.bind('<<ComboboxSelected>>', self.read_monitor_history)

    def create_clear_local_result_dialog(self):
        ttk.Button(self.download_history_mode_frame, text='确认下载', style="blue.TButton",
                   command=self.download_result).pack(side=LEFT, anchor=W, ipadx=20, padx=10)

        ttk.Button(self.download_history_mode_frame, text='取消', style="blue.TButton",
                   command=self.download_history_mode_frame.pack_forget).pack(side=LEFT, anchor=W, ipadx=20, padx=10)

        ttk.Button(self.download_history_mode_frame, text='清除记录', style="red.TButton",
                   command=self.clear_local_monitor_history).pack(side=LEFT, anchor=W, ipadx=20, padx=10)

    def init_monitor(self):
        step = 'InitEnv'
        self.top_master.execute_command(step)

    def run_monitor(self):
        step = 'runJvmMonitor'
        self.top_master.execute_command(step)

    def download_result(self):
        self.download_history_mode_frame.pack_forget()
        download_combobox_selected_value = self.monitor_history_download_combobox.get()
        scene_date = download_combobox_selected_value[6:14]
        scene_time = download_combobox_selected_value[14:18]
        scene_name = download_combobox_selected_value[25:]
        scene_info = {'scene_date': scene_date, 'scene_time': scene_time, 'scene_name': scene_name}
        step = 'DownLoadResult'
        self.top_master.execute_command(step, download_scene_info=scene_info)

    def show_download_widget(self):
        self.download_history_mode_frame.pack(side=LEFT, anchor=W, padx=20)

    def hide_download_widget(self):
        self.download_history_mode_frame.pack_forget()

    def deleteRes(self):
        self.delete_result(self.top_master)

    def clear_local_monitor_history(self):
        logger.debug('clear_page...')
        conf_path_res = 'Result_Monitor.conf'
        message_text = '此操作将删除本地保存的执行记录,不影响服务器和本地的监控结果,\n所有结果后续可通过自定义下载,建议每次项目完成后清理执行记录.\n是否继续?'
        if messagebox.askokcancel('通知!', message_text):
            os.remove(conf_path_res)
            self.top_master.clear_page()
        self.download_history_mode_frame.pack_forget()

    @kill_monitor_confirm
    def kill_monitor(self):
        step = 'killJstat'
        self.top_master.execute_command(step)

    def read_monitor_history(self, *args):
        # logger.debug('read_result...')
        cf = ConfigParser()
        cf.read('Result_Monitor.conf')
        result_id = cf.items('TITLE')
        result_id = list(reversed(result_id))
        self.monitor_history_download_combobox['values'] = result_id
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
