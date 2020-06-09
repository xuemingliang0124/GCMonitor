from tkinter import *
from tkinter.ttk import *


class SceneSetWidget:
    def __init__(self, master):
        self.master = master

    def create_scene_set_widgets(self):
        scene_set_frame = Frame(self.master)
        scene_set_frame.pack(side=TOP, anchor=N, pady=10, fill=X)
        self.scene_set_sub_frame = SceneSetSubFrame(scene_set_frame)
        self.scene_set_sub_frame.create_scene_name_widget()
        self.scene_set_sub_frame.create_scene_time_widget()
        self.scene_set_sub_frame.create_scene_step_widget()
        self.scene_set_sub_frame.create_scene_times_widget()

    def get_scene_info(self):
        return self.scene_set_sub_frame.get_scene_info()


class SceneSetSubFrame():
    def __init__(self, master):
        scene_name_sub_frame = Frame(master)
        scene_name_sub_frame.pack(side=TOP, anchor=W)
        scene_other_sub_frame = Frame(master)
        scene_other_sub_frame.pack(side=TOP, pady=10)
        self.scene_name_frame = Frame(scene_name_sub_frame)
        self.scene_name_frame.pack(side=LEFT, anchor=N, padx=5)

        self.scene_time_frame = Frame(scene_other_sub_frame)
        self.scene_time_frame.pack(side=LEFT, padx=5)

        self.scene_step_frame = Frame(scene_other_sub_frame)
        self.scene_step_frame.pack(side=LEFT, padx=5)

        self.scene_times_frame = Frame(scene_other_sub_frame)
        self.scene_times_frame.pack(side=LEFT, padx=5)

        self.scene_name = StringVar()
        self.scene_times = IntVar()
        self.unit = StringVar()
        self.scene_time_list = ['1小时', '10小时', '12小时', '24小时', '36小时']
        self.scene_time_second_list = [3600, 36000, 43200, 86400, 129600]
        self.scene_step_list = ['10', '30', '60', '120', '300']

    def create_scene_name_widget(self):
        Label(self.scene_name_frame, text='场景名称', width=8).pack(side=LEFT, anchor=W)
        Entry(self.scene_name_frame, text=self.scene_name, width=40).pack(side=LEFT, anchor=W)

    def create_scene_time_widget(self):
        Label(self.scene_time_frame, text='监控时长', width=8).pack(side=LEFT, anchor=W)
        self.scene_time_comb = Combobox(self.scene_time_frame, width=6, state="readonly")
        self.scene_time_comb.pack(side=LEFT, anchor=W)
        self.scene_time_comb['values'] = self.scene_time_list
        self.scene_time_comb.current(0)
        self.scene_time_comb.bind("<<ComboboxSelected>>", self._calculation_monitor_times)

    def create_scene_step_widget(self):
        Label(self.scene_step_frame, text='采集间隔', width=8).pack(side=LEFT, anchor=W)
        self.scene_step_comb = Combobox(self.scene_step_frame, width=3, state="readonly")
        self.scene_step_comb.pack(side=LEFT, anchor=W)
        self.scene_step_comb['values'] = self.scene_step_list
        self.scene_step_comb.current(0)
        self.scene_step_comb.bind("<<ComboboxSelected>>", self._calculation_monitor_times)
        Label(self.scene_step_frame, text='秒', width=4).pack(side=LEFT, anchor=W)

    def create_scene_times_widget(self):
        self.unit.set('次')
        Label(self.scene_times_frame, text='采集次数：', width=8).pack(side=LEFT, anchor=W)
        self.scene_times_label = Label(self.scene_times_frame, textvariable=self.scene_times, width=1)
        self.scene_times_label.pack(side=LEFT, anchor=W)
        Label(self.scene_time_frame, textvariable=self.unit, width=4).pack(side=LEFT, anchor=W)
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
