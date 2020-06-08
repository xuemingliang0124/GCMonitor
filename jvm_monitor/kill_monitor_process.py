import logging
import sys

sys.path.append('..')
from publick_class.execute import Execute

logger = logging.getLogger('XMON.Step_route.KillMonitor')


class KillJstat(Execute):
    def __init__(self, server, infos={}):
        super().__init__(server, infos=infos)
        self.server.create_chan()
        self._kill_proc()
        self._check_proc()
        self.server.exit()

    def _kill_proc(self):
        self.server.exec_cmd(['ps -ef |grep \'jstat\'|grep -v \'grep\'|awk \'{print $2}\'|xargs kill\n'])
        return

    def _check_proc(self):
        check_process_command = ['ps -ef |grep jstat|grep -v \'grep\'|awk \'{print $2}\'\n']
        self.server.exec_cmd(check_process_command)
        process_id_list = self.server.result.strip().split()
        if len(process_id_list) <= 1 and process_id_list[0] is None:
            self.root.set_res('%s\n结束GC监控成功！\n%s\n\n\n' % (self.ip, self.server.result))
            self.tag = 1
        else:
            with self.lock:
                self.root.set_res('%s\n没有找到监控进程，结束GC监控失败！\n%s\n\n\n' % (self.ip, self.server.result), 1)
            return None
