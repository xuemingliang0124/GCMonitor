import logging
import sys

sys.path.append('..')
from public_class.execute import Execute
from decorators import output_log

logger = logging.getLogger('GCMonitor.UI.StepRoute.KillMonitor')


class KillJstat(Execute):
    def __init__(self, server, infos={}):
        super().__init__(server, infos=infos)
        self.server.create_chan()
        self._kill_proc()
        self._check_proc()
        self.server.exit()

    @output_log("KillProcess", logger)
    def _kill_proc(self):
        self.server.exec_cmd(['ps -ef |grep \'jstat\'|grep -v \'grep\'|awk \'{print $2}\'|xargs kill\n'])
        logger.debug(self.server.result)
        return

    @output_log("CheckProcess", logger)
    def _check_proc(self):
        check_process_command = ['ps -ef |grep jstat|grep -v \'grep\'|awk \'{print $2}\'\n']
        self.server.exec_cmd(check_process_command)
        logger.debug(self.server.result)
        process_id_list = self.server.result.strip().split('\n')
        if len(process_id_list) <= 1 and process_id_list[0].startswith('ps -ef'):
            self.root.set_monitor_log('%s\n结束GC监控成功！\n%s\n' % (self.ip, self.server.result))
            self.tag = 1
        else:
            with self.lock:
                self.root.set_monitor_log('%s\n结束GC监控失败,请手动检查！\n%s\n' % (self.ip, self.server.result), 1)
            return None
