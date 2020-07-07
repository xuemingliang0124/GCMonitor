import logging
from public_class import execute
from global_var import SERVER_WORK_FILENAME
from decorators import output_log

logger = logging.getLogger('GCMonitor.UI.StepRoute.InitEnv')


class InitEnvironment(execute.Execute):
    def __init__(self, server, infos):
        super().__init__(server, infos=infos)
        if self.user_permission_check():
            self.process_check()
        self.server.exit()

    @output_log('CheckUser', logger)
    def user_permission_check(self):
        check_command = ['mkdir -p %s\n' % SERVER_WORK_FILENAME, 'find ./ -name %s -type d\n' % SERVER_WORK_FILENAME]
        self.server.exec_cmd(check_command)
        logger.debug(self.server.result)
        if self.server.result.endswith('./%s' % SERVER_WORK_FILENAME):
            return True
        else:
            self.root.set_monitor_log(
                '%s\n监控文件夹创建失败，请检查用户权限！\n执行结果如下：\n%s\n' % (self.server.ip, self.server.result), 1)
            return False

    @output_log('CheckProcess', logger)
    def process_check(self):
        check_command = ['ps -ef |grep java|grep -v "grep"\n']
        self.server.exec_cmd(check_command)
        logger.debug(self.server.result)
        lens = len(self.server.result.split('\n'))
        if lens > 1:
            self.root.set_monitor_log("%s\n初始化完成，检查到以下Java进程，请核对！\n%s\n" % (self.server.ip, self.server.result))
            self.tag = 1
        else:
            self.root.set_monitor_log(
                "%s\n未查询到Java进程，请检查用户权限或确认服务运行状态！\n%s\n" % (self.server.ip, self.server.result), 1)
