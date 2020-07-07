import logging
from sys import exit

import paramiko

from public_class.service_connector import myTrans

logger = logging.getLogger('GCMonitor.UI.StepRoute.Execute')


class Execute(object):
    def __init__(self, server, scene_info={}, infos={}):
        self.ip = server['ip']
        self.port = server['port']
        self.uname = server['uname']
        self.passwd = server['passwd']
        scene_info = scene_info
        if scene_info:
            self.scene_name = scene_info['scene_name']
            self.scene_name = self.scene_name.strip('\n') if self.scene_name else None
            self.scene_step = scene_info['scene_step']
            self.scene_times = scene_info['scene_times']
        self.result_save_path = infos.get('ResultSavePath')
        self.gui_obj = infos.get('gui_obj')
        self.root = self.gui_obj
        self.lock = infos.get('lock')
        self.timestamp = infos.get('timestamp')
        self.error_str = ['No such', 'Not Found', 'not found', 'not allow', 'permission denied', 'ERROR', 'is not',
                          '-bash:', 'ksh:']
        self.tag = 0
        self._connect()

    def _connect(self):
        try:
            self.server = myTrans(self.ip, self.port, self.uname, self.passwd)
            self.server.create_chan()
            logger.debug('create channel finish')
        except paramiko.BadAuthenticationType:
            logger.error('connect to server fialed', exc_info=True)
            self.gui_obj.set_monitor_log('%s\n连接服务器失败!请检查iplist中服务器帐号密码!\n' % self.ip, 1)
            exit(0)
        except paramiko.SSHException:
            logger.error('connect to server fialed', exc_info=True)
            self.gui_obj.set_monitor_log('%s\n连接服务器失败!请检查iplist中服务器地址和端口号!\n' % self.ip, 1)
            exit(0)

    def get_tag(self):
        return self.tag

    def close_connect(self):
        self.server.exit()
