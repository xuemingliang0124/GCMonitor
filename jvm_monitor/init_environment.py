import logging
from publick_class import execute

logger = logging.getLogger("GCMon.StepRoute.InitEnv")


class InitEnvironment(execute.Execute):
    def __init__(self, server, infos):
        super().__init__(server, infos=infos)
        if self.user_permission_check():
            self.process_check()
        self.server.exit()

    def user_permission_check(self):
        check_command = ['mkdir -p monitor\n', 'find ./ -name monitor -type d\n']
        self.server.exec_cmd(check_command)
        if self.server.result.endswith('./monitor'):
            return True
        else:
            self.gui_obj.set_res('%s\n监控文件夹创建失败，请检查用户权限！\n执行结果如下：\n%s\n\n\n' % (self.server.ip, self.server.result), 1)
            return False

    def process_check(self):
        check_command = ['ps -ef |grep java|grep -v "grep"\n']
        self.server.exec_cmd(check_command)
        lens = len(self.server.result.split('\n'))
        if lens > 1:
            self.gui_obj.set_res("%s\n初始化完成，检查到以下Java进程，请核对！\n%s\n\n\n" % (self.server.ip, self.server.result))
            self.tag = 1
        else:
            self.gui_obj.set_res("%s\n未查询到Java进程，请检查用户权限或确认服务运行状态！\n%s\n\n\n" % (self.server.ip, self.server.result), 1)
