import configparser
import datetime
import logging
import os
import re
import sys
import time
from functools import wraps
from PyQt5 import QtWidgets

from gc_monitor_ui.standard_components import StandardMessageBox
from global_var import MONITOR_RECORD, CONFIG_FILE

ip_match = re.compile(r"^((25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(25[0-5]|2[0-4]\d|1?\d?\d)$")


def check_ip_info(func):
    @wraps(func)
    def wrapped_check_ip_info(*args, **kwargs):
        cls = args[0]
        services_info = cls.text_services_info.toPlainText()
        if not services_info:
            QtWidgets.QMessageBox.warning(cls.MainWindow, '错误！', '没有配置服务器信息，请检查！')
            return None
        else:
            services_info = services_info.strip().split('\n')
            services_ip = []
            for index, service_info in enumerate(services_info):
                service_info = service_info.replace("：", ":").split(":")
                if len(service_info) != 3 or not all(service_info):
                    StandardMessageBox(cls.MainWindow, '错误！',
                                       '第%s行目标服务器配置错误，请检查！\n%s' % (index + 1, service_info))
                    return
                ip = service_info[0]
                match_result = ip_match.match(ip)
                if match_result:
                    if ip in services_ip:
                        exists_index = services_ip.index(ip)
                        QtWidgets.QMessageBox.warning(cls.MainWindow, '错误!',
                                                      '第%s行与第%s行IP地址重复,请检查!' % (exists_index + 1, index + 1))
                        return wrapped_check_ip_info
                    else:
                        services_ip.append(ip)
                else:
                    QtWidgets.QMessageBox.warning(cls.MainWindow, '错误！',
                                                  '第%s行目标服务器配置错误，请检查！\n%s' % (index + 1, service_info))
                    return
            else:
                return func(*args, **kwargs)

    return wrapped_check_ip_info


def update_services_info(func):
    @wraps(func)
    def wrapped_set_services_info(*args, **kwargs):
        cls = args[0]
        services_info_path = cls.entry_services_info_path.text()
        if services_info_path:
            services_info = cls.text_services_info.toPlainText()
            with open(services_info_path, 'w') as f:
                f.write(services_info)
        return func(*args, **kwargs)

    return wrapped_set_services_info


def kill_monitor_confirm(func):
    @wraps(func)
    def wrapped_function(*args):
        cls = args[0]
        kill_confirm = StandardMessageBox(cls.MainWindow, '警告！', '此操作将终止监控进程，操作不可逆！是否继续？', '确认', '取消',
                                          QtWidgets.QMessageBox.Question)
        if kill_confirm.clickedButton().text() == '确认':
            func(*args)
        else:
            cls.clear_monitor_log()
            cls.set_monitor_log('操作取消！')

    return wrapped_function


def check_monitor_status(func):
    @wraps(func)
    def wrapped_check_monitor_status(*args):
        if os.path.exists(MONITOR_RECORD):
            cls = args[0]
            now_time = datetime.datetime.fromtimestamp(time.time())
            with open(MONITOR_RECORD, 'r', encoding='utf8') as f:
                monitor_records = f.readlines()
            if monitor_records:
                for monitor_record in monitor_records:
                    if '执行状态:0' in monitor_record:
                        monitor_record_info = monitor_record.split('|')
                        scene_name, timestamp, status, scene_time = map(lambda x: x.split(':')[1].strip(),
                                                                        monitor_record_info)
                        start_timestamp = time.mktime(time.strptime(timestamp, '%Y%m%d%H%M%S'))
                        end_time = datetime.datetime.fromtimestamp(start_timestamp) + datetime.timedelta(
                            seconds=int(scene_time))
                        if end_time <= now_time:
                            monitor_record.replace('执行状态:0', '执行状态:1')
                            continue
                        else:
                            warn_info = '当前有场景未结束，请等待场景结束或终止当前场景！'
                            # name_str = "<font color=\"red\">" + scene_name + "</font>"
                            # start_time_str = "<font color=\"red\">" + timestamp + "</font>"
                            # warn_info = warn_info % (name_str, start_time_str)
                            StandardMessageBox(cls.MainWindow, '警告！', warn_info, '确认', '',
                                               QtWidgets.QMessageBox.Question)
                            return
                else:
                    with open(MONITOR_RECORD, 'w', encoding='utf8') as f:
                        for monitor_record in monitor_records:
                            f.write(monitor_record)
        return func(*args)

    return wrapped_check_monitor_status


def check_download_monitor_status(func):
    @wraps(func)
    def wrapped_func(*args):
        cls = args[0]
        download_monitor = cls.get_download_scene_info()
        if download_monitor == '请选择监控结果:':
            return
        if '执行状态:0' in download_monitor:
            now_time = datetime.datetime.fromtimestamp(time.time())
            monitor_record_info = download_monitor.split('|')
            scene_name, timestamp, status, scene_time = map(lambda x: x.split(':')[1].strip(),
                                                            monitor_record_info)
            start_timestamp = time.mktime(time.strptime(timestamp, '%Y%m%d%H%M%S'))
            end_time = datetime.datetime.fromtimestamp(start_timestamp) + datetime.timedelta(
                seconds=int(scene_time))
            if end_time > now_time:
                warn_info = '当前场景' + "<font color=\"red\">" + scene_name + "</font>" + '未结束，请等待场景结束或终止当前场景！'
                StandardMessageBox(cls.MainWindow, '警告！', warn_info, '确认',
                                   type=QtWidgets.QMessageBox.Question)
                return
        return func(cls)

    return wrapped_func


def check_project_status(func):
    @wraps(func)
    def wrapped_check_project_status(*args):
        cls = args[0]
        service_info_path = cls.entry_services_info_path.text().replace(":", "|")
        if service_info_path:
            cf = configparser.ConfigParser()
            cf.read(CONFIG_FILE, encoding='utf-8-sig')
            project_status = cf.get('PROJECTS', service_info_path)
            if project_status == '0':
                warn_str = '项目尚未初始化或初始化失败，请先执行初始化操作！'
                StandardMessageBox(cls.MainWindow, '警告！', warn_str, '确认', '',
                                   QtWidgets.QMessageBox.Warning)

                return
        return func(*args)

    return wrapped_check_project_status


def output_log(step: str, logger: logging.Logger):
    def dec_output_log(func):
        @wraps(func)
        def wrapped_output_log(*args):
            logger.info("%s start" % step)
            try:
                return func(*args)
            except:
                logger.exception(sys.exc_info())
            finally:
                logger.info("%s end" % step)
            return True

        return wrapped_output_log

    return dec_output_log


def check_workspace_path(func):
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        cls = args[0]
        workspace_path = cls.entry_workspace_path.text()
        if workspace_path:
            if os.path.isfile(workspace_path):
                warn_str = '工作路径不应包含文件名，请重新设置！'
                StandardMessageBox(cls.MainWindow, '工作路径错误', warn_str, '确认')
            elif not os.path.exists(workspace_path):
                warn_str = '没有找到{syspath}，请检查工作路径设置！'.format(syspath=workspace_path)
                StandardMessageBox(cls.MainWindow, '工作路径错误', warn_str, '确认')
            else:
                return func(*args, **kwargs)
        else:
            warn_str = '请先设置工作路径，用于保存监控结果等文件'
            StandardMessageBox(cls.MainWindow, '工作路径错误', warn_str, '确认')

    return wrapped_function


def check_scene_name(func):
    @wraps(func)
    def wrapped_check_scene_name(*args):
        cls = args[0]
        scene_info = cls.get_run_scene_info()
        scene_name = scene_info.get("scene_name")
        if not scene_name:
            StandardMessageBox(cls.MainWindow, '场景名称错误!错误！', '场景名称不能为空！', '确认')
            return False
        zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
        match = zh_pattern.search(scene_name)
        if match:
            StandardMessageBox(cls.MainWindow, '场景名称错误!', '场景名称应由字母、数字或下划线组成!', '确认')
            return False
        # if not scene_info.get('scene_step'):
        #     QtWidgets.QMessageBox.warning(self.MainWindow, '错误!', '采集间隔必须为正整数!')
        #     return False
        # if not scene_info.get('scene_times'):
        #     QtWidgets.QMessageBox.warning(self.MainWindow, '错误!', '采集次数必须为正整数!')
        #     return False
        return func(*args)

    return wrapped_check_scene_name
