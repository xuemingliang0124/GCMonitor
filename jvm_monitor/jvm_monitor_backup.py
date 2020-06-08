import configparser
from functools import partial as pto, wraps
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox
from tkinter import *
from tkinter import ttk
import logging
import os
import sys
import time
import zipfile
from step_route import step_route

sys.path.append('..')
from publick_class.DeleteResult_GUI import DeleteResult_GUI
from publick_class.threads_control import MyThread
from publick_class.ip_list import Iplist

from publick_class import SFTPConfig, VersionConfig

Version = VersionConfig.XMON_Version
creat_time = VersionConfig.XMON_creat_time
# server = myTrans(ip=SFTPConfig.ip, port=SFTPConfig.port, uname=SFTPConfig.uname, passwd=SFTPConfig.passwd)
server_path = SFTPConfig.server_path

# 若配置文件不存在，则生成
conf_path = 'Resource_Monitor.conf'
cf = configparser.ConfigParser()
if os.path.exists(conf_path):
    pass
else:
    conf = {'PATH':
                {'workspace': '',
                 'version_check_path': '/XMON/VersionCheck'},
            'LOG':
                {'LogLevel': 'DEBUG',
                 'FileSize': '2',
                 'LogPath': 'log/resource_result.log'}}
    for sec, opts in conf.items():
        cf.add_section(sec)
        for opt, value in opts.items():
            cf.set(section=sec, option=opt, value=value)
    with open(conf_path, 'w') as f:
        cf.write(f)

# 读取日志配置信息
cf.read(conf_path)
loglevel = cf.get('LOG', 'LogLevel')
filesize = cf.get('LOG', 'FileSize')
log_path = cf.get('LOG', 'LogPath')
version_checkpath = cf.get('PATH', 'version_check_path')


# 日志打包、上传
def handle_log():
    if os.path.exists(log_path):
        size = os.path.getsize(log_path) / 1024 / 1024
        if size >= float(filesize):
            a = os.popen('ipconfig /all')
            b = a.read()
            str = re.compile(r'(?ims): (\d+\.\d+\.\d+\.\d+)\(')
            result = str.search(b)
            name = result.group(1) if result else None
            stamp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            source = log_path
            sourcename = source.split('/')[-1]
            zipname = 'log\\%s_%s_resource_result.zip' % (name, stamp)
            zip = zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED)
            zip.write(source, sourcename)
            zip.close()
            # localpath = 'log'
            # remotepath = os.path.join(server_path, 'XMON/log')
            # filename = '%s_%s_resource_result.zip' % (name, stamp)
            # try:
            #     server.upload(os.path.join(localpath, filename), os.path.join(remotepath, filename))
            #     os.remove(os.path.join(localpath, filename))
            # except:
            #     pass
    else:
        os.makedirs('log')


handle_log()

# 日志设置
logger = logging.getLogger('XMON')
logger.setLevel(level=eval('logging.%s' % loglevel))

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s')

file_handler = logging.FileHandler(log_path)
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.addHandler(file_handler)


def syspathcheck(func):
    @wraps(func)
    def wrapped_function(*args):
        syspath = gui_obj.syspath_var.get()
        if syspath:
            if os.path.isfile(syspath):
                tkMessageBox.showinfo(title='', message='工作路径不应包含文件名，请重新设置！')
            elif not os.path.exists(syspath):
                tkMessageBox.showinfo(title='', message='没有找到{syspath}，请检查工作路径设置！'.format(syspath=syspath))
            else:
                return func(*args)
        else:
            tkMessageBox.showinfo(title='', message='请先设置工作路径，用于保存iplist及监控结果等文件')

    return wrapped_function


def ippathcheck(func):
    @wraps(func)
    def wrapped_function(*args):
        syspath = gui_obj.syspath_var.get()
        for i in os.listdir(syspath):
            if i == 'iplist.xlsx':
                gui_obj.iplist_path = os.path.join(syspath, i)
                return func(*args)
        else:
            gui_obj.set_res('没有找到"{syspath}/iplist.xlsx",请检查工作路径或先点击生成iplist模板并配置服务器ip信息!\n'.format(syspath=syspath))

    return wrapped_function


def askyesno(func):
    @wraps(func)
    def wrapped_function(*args):
        if not tkMessageBox.askokcancel(title='警告！', message='警告：此操作将终止监控进程，操作不可逆！是否继续？'):
            gui_obj.del_res()
            gui_obj.set_res('操作取消！')
        else:
            func(*args)

    return wrapped_function


def scene_check_not_null(func):
    @wraps(func)
    def wrapped_function(*args):
        if not gui_obj.scene_name.get():
            tkMessageBox.showinfo('错误！', '场景名称不能为空！')
            return wrapped_function
        scene_name = gui_obj.scene_name.get()
        zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
        match = zhPattern.search(scene_name)
        if match:
            tkMessageBox.showerror('错误!', '场景名称不可以包含中文或特殊字符!')
            return wrapped_function
        if not gui_obj.scene_step.get():
            tkMessageBox.showerror('错误!', '采集间隔必须为正整数!')
            return wrapped_function
        if not gui_obj.scene_times.get():
            tkMessageBox.showerror('错误!', '采集次数必须为正整数!')
            return wrapped_function
        func(*args)

    return wrapped_function


class Gui(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title('XMON_%s' % Version)
        self.geometry('650x600')
        self.resizable(width=False, height=False)
        menubar = Menu(self)
        menubar.add_command(label='使用说明', font='14', command=self._instruction)
        menubar.add_command(label='版本', font='14', command=self._version)
        self.configure(menu=menubar)
        pwd = os.getcwd()
        self.url = os.path.join(pwd, 'Resource_Monitor.conf')
        self.syspath_var = StringVar()
        if os.path.exists(self.url):
            cf = configparser.ConfigParser()
            cf.read(self.url)
            try:
                self.syspath_var.set(cf.get(section='PATH', option='workspace'))
            except:
                pass
        self.creat_page()
        self._create_frame()
        self._create_prep_widget()
        self._create_run_widget()
        self._create_download_widget()
        self._creat_download_rember()
        self._create_res_widget()
        # VersionCheck.VersionCheck(Version, 'XMON')

    def creat_page(self):
        conf_path_res = 'Result_Monitor.conf'
        if os.path.exists(conf_path_res):
            pass
        else:
            conf = {'TITLE':
                        {'请选择需要下载项目': ':'}}
            cf = configparser.ConfigParser()
            for sec, opts in conf.items():
                cf.add_section(sec)
                for opt, value in opts.items():
                    cf.set(section=sec, option=opt, value=value)
            with open(conf_path_res, 'w') as f:
                cf.write(f)

    def _version(self):
        tkMessageBox.showinfo(title='版本', message=Version + creat_time)

    def _instruction(self):
        a = []
        tpl = Toplevel(self)
        tpl.title('使用说明')
        tpl.geometry('730x340')
        tpl.resizable(width=False, height=False)
        for i in a:
            text = Label(tpl, text=i)
            text.pack(side=TOP, anchor=NW)

    def _create_frame(self):
        self.prep_fr = ttk.LabelFrame(self, text='前置', width=600)
        self.prep_fr.pack(side=TOP, pady=10, fill=X)

        self.ippath_fr = ttk.Frame(self.prep_fr)
        self.ippath_fr.pack(side=TOP, fill=X, padx=10, pady=5)

        self.btn_fr = ttk.Frame(self.prep_fr)
        self.btn_fr.pack(side=LEFT, pady=10, fill=X)

        self.run_fr = ttk.LabelFrame(self, text='场景设置')
        self.run_fr.pack(side=TOP, pady=10, anchor=N, fill=X)

        self.scene_fr = ttk.Frame(self.run_fr)
        self.scene_fr.pack(side=TOP, anchor=N, pady=10, fill=X)

        self.scene_name_fr = ttk.Frame(self.scene_fr)
        self.scene_name_fr.pack(side=LEFT, anchor=N, padx=5)

        self.scene_step_fr = ttk.Frame(self.scene_fr)
        self.scene_step_fr.pack(side=LEFT, padx=5)

        self.scene_times_fr = ttk.Frame(self.scene_fr)
        self.scene_times_fr.pack(side=LEFT, padx=5)

        self.scene_time_fr = ttk.Frame(self.scene_fr)
        self.scene_time_fr.pack(side=LEFT, padx=5)

        self.exe_fr = ttk.Frame(self.run_fr)
        self.exe_fr.pack(side=TOP, pady=10, anchor=N, fill=X)

        self.download_widget = ttk.Frame(self.run_fr)
        self.download_widget.pack_forget()

        self.download_rember_fr = ttk.Frame(self.run_fr)
        self.download_rember_fr.pack_forget()

        self.upgc_widget = ttk.Frame(self.run_fr)
        self.upgc_widget.pack_forget()

        self.res_fr = ttk.LabelFrame(self, text='执行结果')
        self.res_fr.pack(side=TOP, anchor=N, fill=X)

    def _create_prep_widget(self):
        ttk.Label(self.ippath_fr, text='工作路径').pack(side=LEFT, anchor=N)
        self.iplist_path_entr = ttk.Entry(self.ippath_fr, textvariable=self.syspath_var, width=32)
        self.iplist_path_entr.pack(side=LEFT, fill=X, anchor=N)
        ttk.Button(self.ippath_fr, text='浏览...', width=7, command=self._set_path).pack(side=LEFT, anchor=N)
        text = ['生成iplist模板', '编辑iplist.xlsx', '部署监控工具']
        command = ['self._create_file', 'self._open_iplist', 'self._uploadNmon']
        btn = pto(ttk.Button, self.btn_fr, width=10)
        pck_set = 'side=LEFT, anchor=W, ipadx=20, padx=10'
        for i in range(len(text)):
            eval('btn(text="%s", command=%s).pack(%s)' % (text[i], command[i], pck_set))

    def _create_run_widget(self):
        self.scene_name = StringVar()
        self.scene_step = IntVar()
        self.scene_times = IntVar()
        self.mon_time = IntVar()

        ttk.Label(self.scene_name_fr, text='场景名称', width=8).pack(side=LEFT, anchor=W)
        ttk.Entry(self.scene_name_fr, text=self.scene_name, width=20).pack(side=LEFT, anchor=W)

        ttk.Label(self.scene_times_fr, text='采集次数(-c)', width=10).pack(side=LEFT, anchor=W)
        a = ttk.Entry(self.scene_times_fr, text=self.scene_times, width=4)
        a.pack(side=LEFT, anchor=W)
        a.bind('<FocusOut>', self._set_mon_tiem)
        ttk.Label(self.scene_times_fr, text='次', width=4).pack(side=LEFT, anchor=W)

        ttk.Label(self.scene_step_fr, text='采集间隔（-s）', width=10).pack(side=LEFT, anchor=W)
        a = ttk.Entry(self.scene_step_fr, text=self.scene_step, width=4)
        a.pack(side=LEFT, anchor=W)
        a.bind('<FocusOut>', self._set_mon_tiem)
        ttk.Label(self.scene_step_fr, text='秒', width=4).pack(side=LEFT, anchor=W)

        self.unit = StringVar()
        self.unit.set('秒')
        ttk.Label(self.scene_time_fr, text='监控时长：', width=10).pack(side=LEFT, anchor=W)
        self.mon_time_lb = ttk.Label(self.scene_time_fr, textvariable=self.mon_time, width=1)
        self.mon_time_lb.pack(side=LEFT, anchor=W)
        ttk.Label(self.scene_time_fr, textvariable=self.unit, width=4).pack(side=LEFT, anchor=W)

        text = ['启动监控', '下载监控结果并解析', '删除监控结果', '终止监控进程']
        command = ['upnmon', 'show_download_widget', 'deleteRes', 'killnmon']
        btn = pto(ttk.Button, self.exe_fr, width=10)
        pck_set = 'side=LEFT, anchor=W, ipadx=20, padx=10'
        for i in range(len(text)):
            eval('btn(text=text[i], command=self._%s, style="TButton").pack(%s)' % (command[i], pck_set))

    def _creat_download_rember(self):
        logger.debug('create_download_rember...')
        self.result = ttk.Combobox(self.download_rember_fr, width=60, height=20)
        self.read_result()
        lens = len(self.result['values'])
        self.result.pack(side=TOP, padx=5, pady=5)
        self._yesno_res()
        self.result.current(lens - 1)
        self.result.bind('<<ComboboxSelected>>', self.read_result)

    def read_result(self, *args):
        logger.debug('read_result...')
        cf = configparser.ConfigParser()
        cf.read('./Result_Monitor.conf')
        result_id = cf.items('TITLE')
        self.result['values'] = result_id
        self.result['state'] = 'readonly'

    def _yesno_res(self):
        ttk.Button(self.download_rember_fr, text='确认下载',
                   command=self._downloadres_new).pack(side=LEFT, anchor=W, ipadx=20, padx=10)

        ttk.Button(self.download_rember_fr, text='取消',
                   command=self.download_rember_fr.pack_forget).pack(side=LEFT, anchor=W, ipadx=20, padx=10)

        ttk.Button(self.download_rember_fr, text='自定义',
                   command=self._show_upgc_widget).pack(side=LEFT, anchor=W, ipadx=20, padx=10)
        ttk.Button(self.download_rember_fr, text='清除记录',
                   command=self._clear_page).pack(side=LEFT, anchor=W, ipadx=20, padx=10)

    def _clear_page(self):
        logger.debug('clear_page...')
        conf_path_res = 'Result_Monitor.conf'
        if tkMessageBox.askokcancel('通知!', '此操作将删除本地保存的执行记录,不影响服务器和本地的监控结果,'
                                           '\n所有结果后续可通过自定义下载,建议每次项目完成后清理执行记录.\n是否继续?'):
            os.remove(conf_path_res)
            self.creat_page()

    def _create_download_widget(self):
        self._tip()
        self._year_gen()
        self._month_gen()
        self._day_gen()
        self._hour()
        self._minute()
        self._yesno()

    def _tip(self):
        ttk.Label(self.download_widget, text='请选择监控执行日期.具体执行时间选填,若填写不完整则下载当天最新(时间最晚)的监控结果.'
                                             '\n日期或场景名称不对将导致找不到结果文件!',
                  foreground='red').pack(anchor=W, padx=5, pady=5)

    def _hour(self):
        hour_list = ['选填']
        for x in range(0, 24):
            hour_list.append(str(x))
        self.hour = ttk.Combobox(self.download_widget, width=4, state='readonly')
        self.hour['values'] = hour_list
        self.hour.current(0)
        self.hour.pack(side=LEFT)
        ttk.Label(self.download_widget, text='时',
                  width=2).pack(side=LEFT, anchor=W)

    def _minute(self):
        minute_list = ['选填']
        for x in range(60):
            minute_list.append(str(x))
        self.minute = ttk.Combobox(self.download_widget, width=4, state='readonly')
        self.minute['values'] = minute_list
        self.minute.current(0)
        self.minute.pack(side=LEFT)
        ttk.Label(self.download_widget, text='分',
                  width=2).pack(side=LEFT, anchor=W)

    def _day_gen(self, *args):
        self.day = ttk.Combobox(self.download_widget, width=2, state='readonly')
        self.day.pack(side=LEFT)
        ttk.Label(self.download_widget, text='日', width=2).pack(side=LEFT,
                                                                anchor=W)
        self._day_set()

    def _day_set(self, *args):
        y = int(self.year.get())
        m = int(self.month.get())
        today = int(time.strftime('%d', time.localtime()))
        if m == 2:
            if y % 4 == 0 and y % 100 != 0 or y % 400 == 0:
                day_li = [x for x in range(1, 30)]
            else:
                day_li = [x for x in range(1, 29)]
        elif m in [1, 3, 5, 7, 8, 10, 12]:
            day_li = [x for x in range(1, 32)]
        else:
            day_li = [x for x in range(1, 31)]
        self.day['values'] = day_li
        current_day = today if today <= day_li[-1] else 1
        self.day.current(current_day - 1)

    def _month_gen(self, *args):
        month = int(time.strftime('%m', time.localtime()))
        self.month = ttk.Combobox(self.download_widget, width=2, state='readonly')
        self.month_li = [x for x in range(1, 13)]
        self.month['values'] = self.month_li
        self.month.pack(side=LEFT)
        self.month.current(month - 1)
        self.month.bind('<<ComboboxSelected>>', self._day_set)
        ttk.Label(self.download_widget, text='月', width=2).pack(side=LEFT, anchor=W)

    def _year_gen(self, *args):
        date_lab_name = '场景执行日期'
        ttk.Label(self.download_widget, text=date_lab_name,
                  width=11).pack(side=LEFT)
        year = int(time.strftime('%Y', time.localtime()))
        self.year = ttk.Combobox(self.download_widget, width=4, state='readonly')
        self.year_li = [x for x in range(year - 1, year + 1)]
        self.year_li.reverse()
        self.year['values'] = self.year_li
        self.year.pack(side=LEFT, anchor=W)
        self.year.current(0)
        self.year.bind('<<ComboboxSelected>>', self._day_set)
        ttk.Label(self.download_widget, text='年', width=2).pack(side=LEFT, anchor=W)

    def _yesno(self):
        ttk.Button(self.download_widget, text='确认下载',
                   command=self._downloadRes).pack(side=LEFT, anchor=E)
        ttk.Button(self.download_widget, text='取消',
                   command=self.download_widget.pack_forget).pack(side=LEFT,
                                                                  anchor=E)

    def _create_res_widget(self):
        self.res = Text(self.res_fr)
        scrobar = ttk.Scrollbar(self.res_fr)
        self.res.pack(side=LEFT, fill=BOTH, expand=Y)
        self.res.tag_config('red', foreground='red')
        self.res.tag_config('black', foreground='black')
        self.res.configure(yscrollcommand=scrobar.set)
        self.res.configure(state='disabled')
        scrobar.configure(command=self.res.yview)
        scrobar.pack(side=LEFT, fill=Y)

    def _show_download_widget(self):
        self.download_rember_fr.pack(side=LEFT, anchor=W, padx=20)

    def _show_upgc_widget(self):
        self.download_rember_fr.pack_forget()
        self.download_widget.pack(side=LEFT, anchor=W, padx=20)

    def archive(self):
        if self.isup_gc.get():
            self.gc_path_en.configure(state='normal')
        else:
            self.gc_path_en.configure(state='disabled')

    def _set_path(self):
        if self.syspath_var.get():
            init_path = self.syspath_var.get()
        else:
            init_path = os.getcwd()
        path_ = tkFileDialog.askdirectory(initialdir=init_path)
        if path_:
            self.syspath_var.set(path_)
            self._savePath()

    def _set_mon_tiem(self, *args):
        try:
            a = self.scene_step.get()
        except:
            self.scene_step.set(0)
            return 1
        try:
            b = self.scene_times.get()
        except:
            self.scene_times.set(0)
            return 1
        if a and b:
            c = a * b
            if c % 60 == 0:
                if c % 3600 == 0:
                    self.mon_time.set(c / 3600)
                    self.unit.set('小时')
                else:
                    self.mon_time.set(c / 60)
                    self.unit.set('分钟')
            else:
                self.mon_time.set(c)
                self.unit.set('秒')
        self.mon_time_lb['width'] = len(str(self.mon_time.get()))

    @syspathcheck
    def _create_file(self):
        logger.debug('iplist init...')
        syspath = self.syspath_var.get()
        self.iplist_path = os.path.join(syspath, 'iplist.xlsx')
        if os.path.exists(self.iplist_path):
            if not tkMessageBox.askyesno(title='通知！',
                                         message='%s已存在，是否覆盖？'
                                                 % self.iplist_path):
                logger.debug('iplist init cancel')
                self.del_res()
                self.set_res('操作取消！\n')
                return
        logger.debug('iplist init begin')
        Iplist(self.syspath_var.get(), gui_obj).file_init()
        logger.debug('iplist init finish')

    @syspathcheck
    def _open_iplist(self):
        iplist_path = os.path.join(self.syspath_var.get(), 'iplist.xlsx')
        MyThread(os.system, (iplist_path,), 'open_iplist').start()

    @syspathcheck
    @ippathcheck
    def _uploadNmon(self):
        logger.debug('upload nmon...')
        if not self._check_nmon():
            logger.debug('check nmon failed')
            return 0
        logger.debug('check nmon finish')
        step = 'UploadNmon'
        logger.debug('upload nmon begin,step:%s' % step)
        self._execute_command(step)

    @syspathcheck
    @ippathcheck
    @scene_check_not_null
    def _upnmon(self):
        self.download_widget.pack_forget()
        self.download_rember_fr.pack_forget()
        self.upgc_widget.pack_forget()
        step = 'runJvmMonitor'
        logger.debug('upnmon begin,step:%s' % (step))
        self._execute_command(step)

    @syspathcheck
    @ippathcheck
    @askyesno
    def _killnmon(self):
        self.download_widget.pack_forget()
        self.download_rember_fr.pack_forget()
        self.upgc_widget.pack_forget()
        step = 'killJstat'
        logger.debug('KillNmon begin,step:%s' % (step))
        self._execute_command(step)

    @syspathcheck
    @ippathcheck
    def _downloadRes(self):

        logger.debug('download result start')
        if not self.scene_name.get():
            if self.hour.get() == '选填' or self.minute.get() == '选填':
                logger.debug('confirm download...')
                if not tkMessageBox.askyesno('下载确认', '场景名称为空，点击“是”将下载执行日期当天最新监控结果，'
                                                     '按“否”取消下载，是否继续？'):
                    self.del_res()
                    logger.debug('download cancel')
                    self.set_res('操作取消！')
                    return
        step = 'DownLoadResult'
        self.download_widget.pack_forget()
        logger.debug('download begin,step:%s' % step)
        self._execute_command(step)

    @syspathcheck
    @ippathcheck
    def _downloadres_new(self):
        self.download_rember_fr.pack_forget()
        logger.debug('download result_new...')
        a = self.result.get()
        if a == '请选择需要下载项目：':
            tkMessageBox.showinfo(title='通知！', message='请选择正确场景！')
            pass
        else:
            self.CJ_time = a[6:14]
            self.CJ_year = a[6:10]
            self.CJ_moth = a[10:12]
            self.CJ_day = a[12:14]
            self.CJ_hour = a[14:16]
            self.CJ_min = a[16:18]
            self.CJ_name = a[25:]
            step = 'DownLoadResult_new'
            logger.debug('download begin,step:%s' % step)
            self._execute_command(step)

    @syspathcheck
    @ippathcheck
    def _deleteRes(self):
        self.download_widget.pack_forget()
        logger.debug('delete result start')
        DeleteResult_GUI().delete_result(gui_obj)

    def _check_nmon(self):
        logger.debug('download monitor...')
        syspath = self.syspath_var.get()
        # monitors=['nmon','glance.sh','adviser.syntax','net.syntax']
        # tag=[]
        # for i in monitors:
        #     localpath=os.path.join(syspath,i)
        #     remotepath=os.path.join(server_path,'Monitor_Tools/%s'%i)

        if os.path.exists('nmon') and os.path.exists('mysql.monitor'):
            logger.debug('check_nmon finish')
        else:
            logger.error('check_nmon error!', exc_info=1)
            self.set_res('%s路径下没有找到nmon或mysql.monitor文件！' % self.syspath_var.get())
            return 0
        return 1

    def _execute_command(self, step):
        self.del_res()
        iplist = self.iplist_path
        if step == 'DownLoadResult_new':
            step = 'DownLoadResult'
        else:
            self.CJ_name = ''
        scene_info = {'syspath': self.syspath_var.get(),
                      'iplist': iplist, 'step': step,
                      'scene_name': self.scene_name.get(),
                      'scene_step': self.scene_step.get(),
                      'scene_times': self.scene_times.get(),
                      'gui_obj': gui_obj}
        MyThread(step_route, (self.CJ_name, scene_info), step).start()

    def set_res(self, res, tag=None):
        self.res.configure(state='normal')
        if tag:
            self.res.insert(END, res, 'red')
        else:
            self.res.insert(END, res, 'black')
        self.res.see(END)
        self.res.configure(state='disabled')

    def del_res(self):
        logger.debug('clear result')
        self.res.configure(state='normal')
        self.res.delete(0.0, END)
        self.res.update_idletasks()
        self.res.configure(state='disabled')

    def _savePath(self):
        syspath = self.syspath_var.get()
        cf = configparser.ConfigParser()
        cf.read(self.url)
        cf.set('PATH', 'workspace', syspath)
        with open(self.url, 'w') as f:
            cf.write(f)


if __name__ == '__main__':
    gui_obj = Gui()
    gui_obj.mainloop()
