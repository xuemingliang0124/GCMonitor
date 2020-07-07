import logging

from public_class.execute import Execute
from global_var import SERVER_WORK_FILENAME
from decorators import output_log

logger = logging.getLogger('GCMonitor.UI.StepRoute.DeleteResult')


class DeleteResult(Execute):
    def __init__(self, server={}, infos={}):
        super().__init__(server=server, infos=infos)
        self._delete_result()

    @output_log("ClearServices", logger)
    def _delete_result(self):
        self.server.create_chan()
        command = ['\\rm -rf ./%s\n' % SERVER_WORK_FILENAME]
        self.server.exec_cmd(command)
        if 'No such file' in self.server.result or 'Not Found' in self.server.result or 'is not' in self.server.result:
            with self.lock:
                logger.debug('can not find results directory:%s' % self.server.result)
                self.root.set_monitor_log(self.ip + '\n没有找到监控结果文件夹！\n' + self.server.result, 1)
        else:
            with self.lock:
                logger.debug('delete result finished:%s' % self.server.result)
                self.root.set_monitor_log(self.ip + '\n监控结果删除成功！\n' + self.server.result)
            self.tag = 1
        self.server.exit()
