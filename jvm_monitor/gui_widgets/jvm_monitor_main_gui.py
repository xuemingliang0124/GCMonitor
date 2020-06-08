import configparser
from functools import wraps
import tkinter
from tkinter import messagebox
from tkinter import ttk
import logging
import os
import re
from jvm_monitor.step_route import StepRoute

from publick_class.threads_control import MyThread
from jvm_monitor.gui_widgets.prepare_widget import PrepareWidget
from jvm_monitor.gui_widgets.monitor_operation_frame import MonitorOperationFrame
from jvm_monitor.gui_widgets.execution_info_frame import ExecutionInfoFrame
from jvm_monitor.log import jvm_monitor_log
from publick_class import SFTPConfig

MONITOR_HISTORY_FILE = 'Result_Monitor.conf'

jvm_monitor_log.init_config()
VERSION = 'V1.0'
CREATE_TIME = '2020/06/03'
AUTHOR = "薛明亮"
server_path = SFTPConfig.server_path

logger = logging.getLogger('JvmMonitor.GUI')


def syspathcheck(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        syspath = args[0].prepare_widget.get_iplist_path()
        if syspath:
            if os.path.isfile(syspath):
                messagebox.showinfo(title='', message='工作路径不应包含文件名，请重新设置！')
            elif not os.path.exists(syspath):
                messagebox.showinfo(title='', message='没有找到{syspath}，请检查工作路径设置！'.format(syspath=syspath))
            else:
                for i in os.listdir(syspath):
                    if i == 'iplist.xlsx':
                        args[0].iplist_path = os.path.join(syspath, i)
                        args[0].hide_download_widget()
                        return func(*args, **kwargs)
                else:
                    args[0].set_res(
                        '没有找到"{syspath}/iplist.xlsx",请检查工作路径或先点击生成iplist模板并配置服务器ip信息!\n'.format(syspath=syspath))
        else:
            messagebox.showinfo(title='', message='请先设置工作路径，用于保存iplist及监控结果等文件')

    return wrapped_function


def scene_check_not_null(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        if args[1] != 'runJvmMonitor':
            return func(*args, **kwargs)
        scene_info = args[0].monitor_operation_frame.get_scene_info()
        scene_name = scene_info.get('scene_name')
        if not scene_name:
            messagebox.showinfo('错误！', '场景名称不能为空！')
            return wrapped_function
        zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
        match = zh_pattern.search(scene_name)
        if match:
            messagebox.showerror('错误!', '场景名称应由字母、数字或下划线组成!')
            return wrapped_function
        if not scene_info.get('scene_step'):
            messagebox.showerror('错误!', '采集间隔必须为正整数!')
            return wrapped_function
        if not scene_info.get('scene_times'):
            messagebox.showerror('错误!', '采集次数必须为正整数!')
            return wrapped_function
        return func(*args, **kwargs)

    return wrapped_function


class Gui(tkinter.Tk):
    def __init__(self):
        super().__init__()
        # 工具标题
        self.title('GC监控_%s' % VERSION)
        # 设置窗口大小并禁用大小调整
        self.geometry('700x600')
        # self.resizable(width=False, height=False)
        # 菜单栏
        menubar = tkinter.Menu(self)
        # menubar.add_command(label='使用说明', font='14', command=self._instruction)
        menubar.add_command(label='版本', font='14', command=self._version)
        self.configure(menu=menubar)
        # 控件样式设置
        self.style = ttk.Style()
        # 前置部件框架
        self.prepare_widget = PrepareWidget(self)
        # 场景操作部件框架
        self.monitor_operation_frame = MonitorOperationFrame(self)
        # 结果展示部件框架
        self.execute_info_text = ExecutionInfoFrame(self)

    def creat_monitor_history_result_file(self):
        # 监控执行记录文件创建
        if os.path.exists(MONITOR_HISTORY_FILE):
            pass
        else:
            config_item = {'TITLE': {'请选择需要下载项目': ':'}}
            cf = configparser.ConfigParser()
            for sec, opts in config_item.items():
                cf.add_section(sec)
                for opt, value in opts.items():
                    cf.set(section=sec, option=opt, value=value)
            with open(MONITOR_HISTORY_FILE, 'w') as f:
                cf.write(f)

    def style_init(self):
        # self.style.configure("green.TButton", foreground="green", background="green")
        self.style.map("green.TButton",
                       foreground=[("", "green"), ('pressed', 'green2'), ('active', 'green')],
                       # background=[("", "green"), ('pressed', 'green2'), ('active', 'green')]
                       )
        self.style.map("red.TButton",
                       foreground=[("", "red"), ('pressed', 'red2'), ('active', 'red')],
                       # background=[("", "red"), ('pressed', 'red2'), ('active', 'red')]
                       )
        self.style.map("blue.TButton",
                       foreground=[("", "blue"), ('pressed', 'blue2'), ('active', 'blue')],
                       )

    def _version(self):
        version = '版本：%s\n' % VERSION
        author = '作者：%s\n' % AUTHOR
        date = '日期：%s' % CREATE_TIME
        message = version + author + date
        messagebox.showinfo(title='版本', message=message)

    def _instruction(self):
        a = []
        tpl = tkinter.Toplevel(self)
        tpl.title('使用说明')
        tpl.geometry('730x340')
        tpl.resizable(width=False, height=False)
        for i in a:
            text = tkinter.Label(tpl, text=i)
            text.pack(side=tkinter.TOP, anchor=tkinter.NW)

    def create_frame(self):
        # 创建前置工作部件
        self.prepare_widget.create_prepare_widget()
        self.prepare_widget.create_ip_list_button_widget()
        # self.prepare_widget.create_ip_list_show_widget()
        self.prepare_widget.check_workspace()
        # 创建场景设置部件
        self.monitor_operation_frame.create_scene_set_widget()
        self.monitor_operation_frame.create_monitor_operation_widget(self)
        # 创建结果展示部件
        self.execute_info_text.create_execution_info_widget()

    # 读取监控历史记录
    def read_monitor_history(self):
        self.monitor_operation_frame.read_monitor_history()

    # 隐藏下载子部件
    def hide_download_widget(self):
        self.monitor_operation_frame.hide_download_widget()

    # 写入结果展示
    def set_res(self, res, tag=None):
        self.execute_info_text.set_res(res, tag)

    # 清空结果展示
    def del_res(self):
        self.execute_info_text.del_res()

    # 执行用户操作
    @syspathcheck
    @scene_check_not_null
    def execute_command(self, step, download_scene_info=None):
        self.del_res()
        run_scene_info = self.monitor_operation_frame.get_scene_info()
        result_save_path = self.prepare_widget.get_iplist_path()
        step_route = StepRoute(gui_obj, result_save_path, step, run_scene_info, download_scene_info)
        MyThread(step_route.execute, (), step).start()



gui_obj = Gui()
gui_obj.creat_monitor_history_result_file()
gui_obj.style_init()
gui_obj.create_frame()
gui_obj.mainloop()
