import configparser
import sys
from threading import Lock, current_thread
import time

sys.path.append('..')
from publick_class.DeleteResult import *
from publick_class.ip_list import IpList
from publick_class.threads_control import MyThread
from jvm_monitor.init_environment import InitEnvironment
from jvm_monitor.run_jvm_monitor import JvmMonitor
from jvm_monitor.download_result import DownLoadResult
from jvm_monitor.kill_monitor_process import KillJstat
from jvm_monitor.parse_result import ParseResult
from jvm_monitor.delete_result import DeleteResult

logger = logging.getLogger('XMON.Step_route')


class StepRoute():
    def __init__(self, gui_obj, result_save_path, step, run_scene_info=None, download_scene_info=None):
        self.root = gui_obj
        self.result_save_path = result_save_path
        self.step = step
        self.run_scene_info = run_scene_info
        self.download_scene_info = download_scene_info
        self.timestamp = time.localtime()
        self.lock = Lock()
        self.servers = []
        self.local_result_path = ''
        self.result_name = ''
        self.kwargs = {'lock': self.lock, 'timestamp': self.timestamp, 'gui_obj': self.root,
                       'ResultSavePath': self.result_save_path, 'step_route': self}

    def execute(self):
        run_object = self.get_step_object(self.step)
        try:
            self.servers = IpList(self.result_save_path, self.root).read_file()
        except:
            self.root.set_res('打开iplist失败！\n', 1)
            return 0
        self.root.set_res('执行中。。。\n')
        threads = []
        all_run_object = []
        for server in self.servers:
            temp = run_object(server, self.download_scene_info, self.run_scene_info, self.kwargs)
            all_run_object.append(temp)
            t = MyThread(temp.execute, (), server['ip'])
            threads.append(t)
        for i in threads:
            i.start()
        for i in threads:
            i.join()
        self.tags = [i.tag for i in all_run_object]
        success = self.tags.count(1)
        failed = self.tags.count(0)
        self.root.set_res('\n执行完成!\n')
        self.root.set_res('\n共执行成功%s台，失败%s台\n\n\n' % (success, failed))
        if self.step == 'runJvmMonitor':
            self.write_monitor_scene_info()
            self.root.read_monitor_history()
        if self.step == 'DownLoadResult':
            if failed:
                self.root.set_res('\n监控结果下载异常，请检查！\n')
                return
            self.root.set_res('\n 下载完成，解析中。。。\n\n\n')
            if self.local_result_path and self.result_name:
                parse_thread = MyThread(ParseResult, (self.local_result_path, self.result_name, self.root),
                                        'ParseResult')
                parse_thread.start()
                parse_thread.join()
            else:
                self.root.set_res('\n监控结果下载异常，请检查！\n')

    def exe_cls(self, server):

        if 'DownLoad' in self.step:
            var_str = 'self.CJ_name,server,self.scene_info,kwargs'
        else:
            var_str = 'server,self.scene_info,kwargs'
        cmd = '%s(%s)' % (self.step, var_str)
        exe_result = eval(cmd)
        if exe_result.tag:
            self.tags.append(1)
        else:
            self.tags.append(0)
        if 'DownLoad' in self.step:
            self.local_result_path = exe_result.local_result_path
            self.result_name = exe_result.result_name[0]
        if self.step == 'runJvmMonitor':
            self.write_monitor_scene_info()
            self.root.read_result()

    def get_step_object(self, step):
        if self.step == 'runJvmMonitor':
            run_object = RunJvmMonitor
        elif self.step == 'DownLoadResult':
            run_object = RunDownloadResult
        elif self.step == 'killJstat':
            run_object = RunKillMonitor
        elif self.step == 'DeleteResult':
            run_object = JvmDeleteResult
        elif self.step == 'InitEnv':
            run_object = InitEnv
        else:
            run_object = RunJvmMonitor
        return run_object

    def write_monitor_scene_info(self):
        cf = configparser.ConfigParser()
        cf.read('./Result_Monitor.conf')
        times_all = time.strftime('%Y%m%d%H%M%S', self.timestamp)
        times = time.strftime('%Y%m%d%H%M', self.timestamp)
        cf.set('TITLE', '执行时间为：%s' % times_all, '场景名：%s' % self.run_scene_info['scene_name'])
        with open('./Result_Monitor.conf', 'w') as f:
            cf.write(f)

    def set_local_result_path(self, local_result_path, result_name):
        self.local_result_path = local_result_path
        self.result_name = result_name


class OperationBasic:
    def __init__(self, server, download_info, run_scene_info, kwargs):
        self.server = server
        self.kwargs = kwargs
        self.tag = 0

    def execute(self):
        pass

    def set_tag(self, tag):
        self.tag = tag

    def get_tags(self):
        return self.tag


class InitEnv(OperationBasic):
    def execute(self):
        execute = InitEnvironment(self.server, self.kwargs)
        self.set_tag(execute.tag)


class RunJvmMonitor(OperationBasic):
    def __init__(self, server, download_info, run_scene_info, kwargs):
        super().__init__(server, download_info, run_scene_info, kwargs)
        self.server = server
        self.run_scene_info = run_scene_info
        self.kwargs = kwargs

    def execute(self):
        execute = JvmMonitor(self.server, self.run_scene_info, self.kwargs)
        self.set_tag(execute.tag)


class RunDownloadResult(OperationBasic):
    def __init__(self, server, download_info, run_scene_info, kwargs):
        super().__init__(server, download_info, run_scene_info, kwargs)
        self.download_scene_info = download_info

    def execute(self):
        execute = DownLoadResult(self.server, self.download_scene_info, self.kwargs)
        execute.download()
        self.set_tag(execute.tag)


class RunKillMonitor(OperationBasic):
    def execute(self):
        execute = KillJstat(self.server, self.kwargs)
        self.set_tag(execute.tag)


class JvmDeleteResult(OperationBasic):
    def execute(self):
        execute = DeleteResult(self.server, self.kwargs)
        self.set_tag(execute.tag)
