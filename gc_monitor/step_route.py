import logging
from threading import Lock
import os
import time

from global_var import MONITOR_RECORD
from public_class.threads_control import MyThread
from gc_monitor.init_environment import InitEnvironment
from gc_monitor.run_jvm_monitor import JvmMonitor
from gc_monitor.download_result import DownLoadResult
from gc_monitor.kill_monitor_process import KillJstat
from gc_monitor.parse_result import ParseResult
from gc_monitor.delete_result import DeleteResult

logger = logging.getLogger('GCMonitor.UI.StepRoute')


class StepRoute():
    def __init__(self, gui_obj, result_save_path, step, servers, run_scene_info=None,
                 download_scene_info=None):
        self.root = gui_obj
        self.result_save_path = result_save_path
        self.step = step
        self.servers = servers
        self.run_scene_info = run_scene_info
        self.timestamp = time.strftime('%Y%m%d%H%M%S', time.localtime())
        self.lock = Lock()
        self.download_scene_info = download_scene_info
        if download_scene_info:
            scene_name = download_scene_info.get('scene_name')
            scene_date = download_scene_info.get('scene_date')
            self.result_name = '%s_%s' % (scene_name, scene_date)
            self.local_result_path = os.path.join(self.result_save_path, 'test_result', self.result_name)
        self.kwargs = {'lock': self.lock, 'timestamp': self.timestamp, 'gui_obj': self.root,
                       'ResultSavePath': self.result_save_path, 'step_route': self}

    def execute(self):
        run_object = self.get_step_object()
        self.root.set_monitor_log('%s执行中。。。\n' % run_object.name)
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
        self.root.set_monitor_log(
            '%s执行完成!\n共%s台服务器\n成功%s   失败%s\n' % (
                run_object.name, len(self.tags), success, failed))
        if self.step == 'InitEnv' and not failed:
            self.root.set_project_status('1')
        if self.step == 'runJvmMonitor':
            self.write_monitor_scene_info()
            self.root.update_monitor_record()
        if self.step == 'killJstat':
            with open(MONITOR_RECORD, 'r', encoding='utf8') as f:
                content = f.read()
            content = content.replace('执行状态:0', '执行状态:2')
            with open(MONITOR_RECORD, 'w', encoding='utf8') as f:
                f.write(content)
            self.root.update_monitor_record()
        if self.step == 'DownLoadResult':
            if failed:
                self.root.set_monitor_log('控结果下载异常，请检查！\n')
                return
            self.root.set_monitor_log('下载完成，分析结果中，请稍候。。。\n')
            if self.local_result_path and self.result_name:
                parse_thread = MyThread(ParseResult, (self.local_result_path, self.result_name, self.root),
                                        'ParseResult')
                parse_thread.start()
                parse_thread.join()
            else:
                self.root.set_monitor_log('监控结果下载异常，请检查！\n')
        if self.step == 'DeleteResult':
            self.root.set_project_status('0')

    def get_step_object(self):
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
        status = 0
        if self.tags.count(0) > 0:
            status = 3
        monitor_record = "场景名称:%s | 执行时间:%s | 执行状态:%s | 监控时长:%s\n" % (
            self.run_scene_info['scene_name'], self.timestamp, status, self.run_scene_info['scene_time'])
        with open(MONITOR_RECORD, 'a', encoding="utf8") as f:
            f.write(monitor_record)

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
    name = '初始化监控'

    def execute(self):
        execute = InitEnvironment(self.server, self.kwargs)
        self.set_tag(execute.tag)


class RunJvmMonitor(OperationBasic):
    name = '启动监控'

    def __init__(self, server, download_info, run_scene_info, kwargs):
        super().__init__(server, download_info, run_scene_info, kwargs)
        self.server = server
        self.run_scene_info = run_scene_info
        self.kwargs = kwargs

    def execute(self):
        execute = JvmMonitor(self.server, self.run_scene_info, self.kwargs)
        self.set_tag(execute.tag)


class RunDownloadResult(OperationBasic):
    name = '下载监控结果'

    def __init__(self, server, download_info, run_scene_info, kwargs):
        super().__init__(server, download_info, run_scene_info, kwargs)
        self.download_scene_info = download_info

    def execute(self):
        execute = DownLoadResult(self.server, self.download_scene_info, self.kwargs)
        execute.download()
        self.set_tag(execute.tag)


class RunKillMonitor(OperationBasic):
    name = '终止监控'

    def execute(self):
        execute = KillJstat(self.server, self.kwargs)
        self.set_tag(execute.tag)


class JvmDeleteResult(OperationBasic):
    name = '清理服务器'

    def execute(self):
        execute = DeleteResult(self.server, self.kwargs)
        self.set_tag(execute.tag)
