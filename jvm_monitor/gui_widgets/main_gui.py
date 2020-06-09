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
from jvm_monitor.gui_widgets.main_frame import main_frame
from jvm_monitor.log import operation_log
from publick_class import SFTPConfig

MONITOR_RECORD = 'MonitorRecord.txt'

operation_log.init_config()
VERSION = 'V1.0'
CREATE_TIME = '2020/06/03'
AUTHOR = "薛明亮"
server_path = SFTPConfig.server_path

logger = logging.getLogger('JvmMonitor.GUI')


def syspathcheck(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        ip_info = args[0].get_ip_info().strip()

        workspace_path = args[0].get_workspace_path()
        if workspace_path:
            if os.path.isfile(workspace_path):
                messagebox.showinfo(title='', message='工作路径不应包含文件名，请重新设置！')
            elif not os.path.exists(workspace_path):
                messagebox.showinfo(title='', message='没有找到{syspath}，请检查工作路径设置！'.format(syspath=workspace_path))
            elif not ip_info:
                messagebox.showinfo(title='', message='没有配置服务器信息，请检查！')
            else:
                return func(*args, **kwargs)
        else:
            messagebox.showinfo(title='', message='请先设置工作路径，用于保存监控结果等文件')

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
        # self.geometry('1000x600')
        self.resizable(width=False, height=False)
        # 菜单栏
        menubar = tkinter.Menu(self)
        # menubar.add_command(label='使用说明', font='14', command=self._instruction)
        menubar.add_command(label='版本', font='14', command=self._version)
        self.configure(menu=menubar)
        # 控件样式设置
        self.style = ttk.Style()

    def create_monitor_history_result_file(self):
        # 监控执行记录文件创建
        if os.path.exists(MONITOR_RECORD):
            pass
        else:
            tips = "请选择下载项目："
            with open(MONITOR_RECORD, 'w', encoding="utf8") as f:
                f.write(tips)

    def style_init(self):
        self.style.map("green.TButton",
                       foreground=[("", "green"), ('pressed', 'green2'), ('active', 'green')],
                       )
        self.style.map("red.TButton",
                       foreground=[("", "red"), ('pressed', 'red2'), ('active', 'red')],
                       )
        self.style.map("blue.TButton",
                       foreground=[("", "blue"), ('pressed', 'blue2'), ('active', 'blue')],
                       )
        self.style.map("springgreen.TButton",
                       foreground=[("", "springgreen"), ('pressed', 'springgreen'), ('active', 'springgreen')],
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
        outside_frame = ttk.Frame(self)
        outside_frame.pack(padx=10, ipady=10)
        self.main_frame = main_frame.MainFrame(outside_frame)
        self.main_frame.create_main_set_widgets(self)
        self.main_frame.create_operation_log_widgets()

    def get_ip_info(self):
        return self.main_frame.get_ip_info()

    def get_workspace_path(self):
        return self.main_frame.get_workspace_path()

    # 读取监控历史记录
    def read_monitor_history(self):
        self.monitor_operation_frame.read_monitor_history()

    # 隐藏下载子部件
    def hide_download_widget(self):
        self.monitor_operation_frame.hide_download_widget()

    # 写入结果展示
    def set_res(self, res, tag=None):
        self.main_frame.set_monitor_log(res, tag)

    # 清空结果展示
    def del_res(self):
        self.main_frame.delete_monitor_log()

    # 执行用户操作
    @syspathcheck
    @scene_check_not_null
    def execute_command(self, step, download_scene_info=None):
        self.del_res()
        run_scene_info = self.main_frame.get_scene_info()
        result_save_path = self.main_frame.get_workspace_path()
        step_route = StepRoute(gui_obj, result_save_path, step, run_scene_info, download_scene_info)
        MyThread(step_route.execute, (), step).start()


if __name__ == '__main__':
    gui_obj = Gui()
    gui_obj.create_monitor_history_result_file()
    gui_obj.style_init()
    gui_obj.create_frame()
    gui_obj.mainloop()
