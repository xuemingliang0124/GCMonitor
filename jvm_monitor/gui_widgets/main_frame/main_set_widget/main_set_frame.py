from tkinter import *
from tkinter.ttk import *
from jvm_monitor.gui_widgets.main_frame.main_set_widget import workspace_set_widget, service_set_widget, \
    scene_set_widget, operation_widget


class MainSetFrame:
    def __init__(self, master):
        self.master = master
        self.workspace_set_frame = LabelFrame(self.master, text="工作区设置")
        self.workspace_set_frame.pack(side=TOP, anchor=W, pady=5)
        self.service_set_frame = LabelFrame(self.master, text="目标服务器设置")
        self.service_set_frame.pack(side=TOP, anchor=W, pady=5)
        self.scene_set_frame = LabelFrame(self.master, text="GC监控设置区")
        self.scene_set_frame.pack(side=TOP, anchor=W, pady=5)
        self.operation_frame = LabelFrame(self.master, text="监控运行控制区")
        self.operation_frame.pack(side=TOP, anchor=W, pady=5)

        self.workspace_set_widgets = workspace_set_widget.WorkspaceSetWidget(self.workspace_set_frame)
        self.service_set_widgets = service_set_widget.ServiceSetWidgets(self.service_set_frame)
        self.scene_set_widgets = scene_set_widget.SceneSetWidget(self.scene_set_frame)

    def create_workspace_set_widgets(self):
        self.workspace_set_widgets.create_workspace_set_widgets()

    def create_service_set_widgets(self):
        self.service_set_widgets.create_path_entry_widgets()
        self.service_set_widgets.create_ip_info_show_widgets()

    def create_scene_set_widgets(self):
        self.scene_set_widgets.create_scene_set_widgets()

    def create_operation_widgets(self, top_master):
        operation_widgets = operation_widget.OperationWidget(self.operation_frame, top_master)
        operation_widgets.create_run_monitor_widget()
        operation_widgets.create_download_history_widget()
        operation_widgets.create_clear_local_result_dialog()
        operation_widgets.create_end_monitor_widget()

    def get_ip_info(self):
        return self.service_set_widgets.get_ip_info()

    def get_workspace_path(self):
        return self.workspace_set_widgets.get_workspace_path()

    def get_scene_info(self):
        return self.scene_set_widgets.get_scene_info()
