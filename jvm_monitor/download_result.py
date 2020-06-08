import logging
import os
import re
import sys

sys.path.append('..')
from publick_class.execute import Execute

logger = logging.getLogger('XMON.Step_route.DownloadResult')


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

    def download(self):
        monitor_date = self.scene_date
        monitor_time = self.scene_time
        scene_name = self.scene_name
        file_name = '"*_%s_%s%s_*.%s"' % (
            scene_name, monitor_date, monitor_time, self.server.mon_file_type)
        command = [
            'find ./monitor/mon_result/%s/ -name %s\n' % (
                monitor_date, file_name
            )
        ]
        logger.debug(command)
        self.result_name = []
        try:
            self.server.exec_cmd(command)
        except UnicodeDecodeError:
            self.root.set_res(
                '\n%s下载失败，未识别服务器编码格式！\n\n\n' % self.ip, 1
            )
            raise
        check_result = self.server.result.split('\r\n')[1:]
        for i in check_result[:]:
            if not i.endswith('.%s' % self.server.mon_file_type) and not i.startswith('NET_'):
                check_result.remove(i)
        mon_type = {'nmon': 'nmon', 'csv': 'glance', 'gc': 'GC', 'monitor': 'MySQL'}
        if check_result is None:
            with self.lock:
                self.root.set_res(
                    '%s\没有找到%s监控结果文件\n%s\n\n' % (
                        self.ip, mon_type[self.server.mon_file_type],
                        self.server.result
                    ), 1
                )
            self.server.exit()
            return 0
        result_infos = []
        for i in check_result:
            if i.endswith(
                    '%s' % self.server.mon_file_type
            ):
                result_date = self.reg_str.search(i)
                if result_date:
                    results = {
                        'server_result_path': result_date.group(1),
                        'result_name': result_date.group(2),
                        'Jserver_name': result_date.group(3),
                        'scene_name': result_date.group(4),
                        'result_date': result_date.group(5)
                    }
                    result_infos.append(results)
        max_result_date = str(max(int(x['result_date']) for x in result_infos))
        for i in result_infos[:]:
            if max_result_date != i['result_date']:
                result_infos.remove(i)
        local_result_path = os.path.join(
            self.result_save_path, 'test_result', monitor_date,
            '%s_%s' % (result_infos[0]['scene_name'],
                       result_infos[0]['result_date'])
        )
        if not self.step_route.local_result_path:
            self.set_local_result_path(local_result_path, self.result_name)
        with self.lock:
            if not os.path.exists(local_result_path):
                os.makedirs(local_result_path)
        for result_info in result_infos:
            try:
                self.server.download(
                    os.path.join(local_result_path,
                                 result_info['result_name']),
                    result_info['server_result_path']
                )
                self.result_name.append(result_info['result_name'])
            except Exception:
                self.tag = 0
                with self.lock:
                    self.root.set_res(
                        '\n%s\n下载失败\n\n\n' % result_info['result_name']
                    )
        with self.lock:
            self.root.set_res('%s\n' % self.ip)
            for i in self.result_name:
                self.root.set_res('%s\n' % i)
                self.root.set_res('下载完成\n\n')
        self.tag = 1
        self.server.exit()

    def init_time(self, values):
        return '0' + str(values) if int(values) < 10 else str(values)

    def set_local_result_path(self, local_result_path, result_name):
        self.step_route.set_local_result_path(local_result_path, result_name)

