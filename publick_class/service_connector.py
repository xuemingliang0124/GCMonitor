import paramiko
from time import sleep
import re
import os


class myTrans(object):
    def __init__(self, ip=None, port=22, uname=None, passwd=None):
        self.ip = ip
        self.port = port
        self.uname = uname
        self.passwd = passwd
        self.code = None
        self.key_path = 'M18_Production.pem'
        self._connect()
        # try:
        #     self._connect_with_key()
        # except Exception:
        #     self._connect()
        # self._connect_with_key(key)

    # 连接服务器并验证身份
    def _connect(self):
        trans = paramiko.Transport((self.ip, int(self.port)))
        trans.start_client()
        trans.auth_password(self.uname, self.passwd)
        self.__trans = trans

    def _connect_with_key(self):
        privatekey = os.path.expanduser(self.key_path)
        key = paramiko.RSAKey.from_private_key_file(privatekey)
        trans = paramiko.Transport((self.ip, int(self.port)))
        trans.start_client()
        trans.auth_publickey(key=key, username=self.uname)
        self.__trans = trans

    #
    def download(self, localpath=None, serverpath=None):
        self.sftp = paramiko.SFTPClient.from_transport(self.__trans)
        self.sftp.get(serverpath, localpath)
        return 1

    #
    def upload(self, localpath, serverpath):
        self.sftp = paramiko.SFTPClient.from_transport(self.__trans)
        self.sftp.put(localpath, serverpath)
        return 1

    def create_chan(self):
        self.chan = self.__trans.open_session()
        self.chan.get_pty()
        self.chan.invoke_shell()
        command = [u'export PS1=">"\n', u'uname\n']
        self.exec_cmd(command)
        self.sysname = re.search(r'(Linux|AIX|HP-UX)', self.result).group(1)
        self.exec_cmd(['locale\n'])
        code_reg = re.search(r'LANG=(\w+?)*\.(.+?)\r*\n', self.result)
        self.code = code_reg.group(2) if code_reg else None
        if self.sysname == 'Linux':
            self.ps = 'ps -ef | grep --color=never'
            self.monitor_file = self.monitor = 'nmon'
            self.mon_cmd = './monitor/%s' % self.monitor
            self.mon_file_type = 'nmon'
        elif self.sysname == 'AIX':
            self.monitor_file = self.monitor = 'nmon'
            self.ps = 'ps -ef | grep '
            self.mon_cmd = self.monitor
            self.mon_file_type = 'nmon'
        else:
            self.monitor = 'glance'
            self.monitor_file = '%s.sh' % (self.monitor)
            self.ps = 'ps -efx | grep'
            self.mon_cmd = './%s.sh' % self.monitor
            self.mon_file_type = 'csv'

    def exec_cmd(self, command: list, endstr=">", code=None):
        self.cmd = command
        result = ''
        for i in self.cmd:
            self.chan.send(i)
            while True:
                sleep(0.5)
                res = self.chan.recv(65535)
                if code:
                    res = res.decode(code, 'replace')
                    res = res.encode()
                    res = str(res, encoding='utf-8')
                elif self.code:
                    res = res.decode(self.code, 'replace')
                    res = res.encode()
                    res = str(res, encoding='utf-8')
                else:
                    res = str(res, encoding='utf-8')
                result += res
                if res.endswith(endstr) or res.endswith('SQL> ') or res.endswith('Enter user-name: '):
                    break
        result = re.sub('\r\n>$', '', result)
        self.result = result

    def func_ps(self, keyword):
        if self.sysname == 'Linux':
            return self.exec_cmd(['ps -ef | grep --color=never "%s"|grep -v "grep"\n' % keyword])
        if self.sysname == 'AIX':
            return self.exec_cmd(['ps -ef | grep "%s"|grep -v "grep"\n' % keyword])
        else:
            return self.exec_cmd(['ps -efx | grep "%s"|grep -v "grep"\n' % keyword])

    def mkdir(self, path):
        return self.exec_cmd(['mkdir -p "%s"\n' % path])

    def exit(self):
        self.__trans.close()
