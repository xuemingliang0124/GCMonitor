import logging

from publick_class.execute import Execute

logger = logging.getLogger('XMON.Step_route.DeleteResult')


class DeleteResult(Execute):
    def __init__(self, server={}, infos={}):
        super().__init__(server=server, infos=infos)
        self._delete_result()

    def _delete_result(self):
        self.server.create_chan()
        command = ['\\rm -rf ./monitor\n']
        self.server.exec_cmd(command)
        logger.debug('delete results directory:%s' % self.server.result)
        if 'No such file' in self.server.result or 'Not Found' in self.server.result or 'is not' in self.server.result:
            with self.lock:
                logger.debug('can not find results directory:%s' % self.server.result)
                self.root.set_res(self.ip + '\n没有找到监控结果文件！\n' + self.server.result, 1)
        else:
            with self.lock:
                logger.debug('delete result finished:%s' % self.server.result)
                self.root.set_res(self.ip + '\n监控结果删除成功！\n' + self.server.result)
            self.tag = 1
        self.server.exit()
