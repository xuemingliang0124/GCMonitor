from tkinter import *
from tkinter.ttk import *
from jvm_monitor.gui_widgets.main_frame.main_set_widget import main_set_frame
from jvm_monitor.gui_widgets.main_frame.operation_log_widget import execution_info_frame


class MainFrame:
    def __init__(self, master):
        self.master = master
        self.main_set_frame = Frame(self.master)
        self.main_set_frame.pack(side=LEFT, fill=Y)
        self.operation_log_frame = Frame(self.master)
        self.operation_log_frame.pack(side=LEFT, anchor=N, fill=Y, expand=1)
        self.main_set_widgets = main_set_frame.MainSetFrame(self.main_set_frame)
        self.operation_log_widgets = execution_info_frame.ExecutionInfoFrame(self.operation_log_frame)

    def create_main_set_widgets(self, top_master):
        self.main_set_widgets.create_workspace_set_widgets()
        self.main_set_widgets.create_service_set_widgets()
        self.main_set_widgets.create_scene_set_widgets()
        self.main_set_widgets.create_operation_widgets(top_master)

    def create_operation_log_widgets(self):
        self.operation_log_widgets.create_execution_info_widget()

    def get_ip_info(self):
        return self.main_set_widgets.get_ip_info()

    def get_workspace_path(self):
        return self.main_set_widgets.get_workspace_path()

    def set_monitor_log(self, res, tag):
        self.operation_log_widgets.set_mongitor_log(res, tag)

    def delete_monitor_log(self):
        self.operation_log_widgets.delete_monitor_log()

    def get_scene_info(self):
        self.main_set_widgets.get_scene_info()
