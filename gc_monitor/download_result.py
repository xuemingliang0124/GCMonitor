import logging
import os
import re
import sys

sys.path.append('..')
from public_class.execute import Execute
from global_var import SERVER_WORK_FILENAME
from decorators import output_log

logger = logging.getLogger('GCMonitor.UI.StepRoute.DownloadResult')


class DownLoadResult(Execute):
    def __init__(self, server, download_scene_info={}, infos={}):
        super().__init__(server, infos=infos)
        self.reg_str = re.compile(r'(\..+?/\d+/((.+_|)\d+\.\d+\.\d+\.\d+_(.+)_(\d{12})_\d*?\.gc))')
        self.server.mon_file_type = 'gc'
        self.download_scene_info = download_scene_info
        self.result_save_path = infos['ResultSavePath']
        self.step_route = infos['step_route']
        self.scene_name = download_scene_info.get('scene_name')
        self.scene_date = download_scene_info.get('scene_date')
        self.scene_time = download_scene_info.get('scene_time')
        self.file_path = "%s_%s" % (self.scene_name, self.scene_date)
        self.remote_file_path = './{server_filename}/mon_result/{file_path}/'.format(
            server_filename=SERVER_WORK_FILENAME,
            file_path=self.file_path)

    def download(self):
        find_files = self.find_files()
        if not find_files:
            with self.lock:
                self.root.set_monitor_log('%s\没有找到gc监控结果文件\n%s\n' % (self.ip, self.server.result), 1)
            self.server.exit()
            return 0
        local_result_save_path = self.create_local_save_path()
        self.download_all_file(find_files, local_result_save_path)

    @output_log("FindFiles", logger)
    def find_files(self):
        file_name = '"*_%s_%s_*.gc"' % (
            self.scene_name, self.scene_date)
        command = [
            'find {remote_file_path} -name {file_name} -exec basename {a} \\;\n'.format(
                remote_file_path=self.remote_file_path,
                file_name=file_name, a='{}')
        ]
        self.result_name = []
        try:
            self.server.exec_cmd(command)
            logger.debug(self.server.result)
        except UnicodeDecodeError:
            self.root.set_monitor_log(
                '\n%s下载失败，未识别服务器编码格式！\n' % self.ip, 1
            )
            raise
        find_files = self.server.result.split('\r\n')[1:]
        return find_files

    @output_log("CreateLocalSavePath", logger)
    def create_local_save_path(self):
        local_result_path = os.path.join(self.result_save_path, 'test_result',self.file_path)
        local_result_path = local_result_path.replace('/', '\\')
        with self.lock:
            if not os.path.exists(local_result_path):
                os.makedirs(local_result_path)
                logger.debug(local_result_path)
        return local_result_path

    @output_log("DownloadAllFiles", logger)
    def download_all_file(self, find_files: list, local_result_path: str):
        for file in find_files:
            try:
                serverpath = os.path.join(self.remote_file_path, file)
                localpath = os.path.join(local_result_path, file)
                self.server.download(serverpath=serverpath, localpath=localpath)
                self.result_name.append(file)
                logger.debug('service path:' + serverpath)
                logger.debug('local path:' + localpath)
            except Exception as e:
                self.tag = 0
                with self.lock:
                    self.root.set_monitor_log('%s\n下载失败\n%s' % (file, e))
        with self.lock:
            self.root.set_monitor_log('%s\n' % self.ip)
            for i in self.result_name:
                self.root.set_monitor_log('%s\n' % i)
                self.root.set_monitor_log('下载完成\n')
        self.tag = 1
        self.server.exit()
