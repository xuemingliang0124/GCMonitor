import logging
import time

from publick_class.execute import Execute
from global_var import SERVER_WORK_FILENAME
from decorators import output_log

logger = logging.getLogger('GCMonitor.UI.StepRoute.RunMonitor')


class JvmMonitor(Execute):
    def __init__(self, *args):
        super().__init__(*args)
        self.file_path = '%s_%s' % (self.scene_name, self.timestamp)
        self.create_filepath()
        self.upmonitor()

    @output_log("CreateFilepath", logger)
    def create_filepath(self):
        path = './%s/mon_result/%s_%s' % (SERVER_WORK_FILENAME, self.scene_name, self.timestamp)
        command = ['mkdir -p %s\n' % path]
        self.server.exec_cmd(command)
        for i in self.error_str:
            if i.lower() not in self.server.result.lower():
                pass
            else:
                self.root.set_monitor_log('%s\n创建文件夹失败！\n%s' % (self.ip, self.server.result))
                self.server.exit()
                exit(0)
        logger.debug("create result filepath\n" + self.server.result)
        self.result_path = path

    @output_log("UpMonitor", logger)
    def upmonitor(self):
        # 查询java进程
        find_java_process_id_command = ['ps -ef |grep java|grep -v \'grep\'|awk \'{print $2}\'\n']
        self.server.exec_cmd(find_java_process_id_command)
        # 判断是否存在Java进程，不存在直接结束
        java_process_id_list = self.server.result.strip().split('\n')[1:]
        if len(java_process_id_list) < 1:
            logger.debug("up monitor failed\n" + self.server.result)
            with self.lock:
                self.root.set_monitor_log(
                    '%s\nGC监控启动失败，没有找到Java进程！\n%s\n' % (self.ip, self.server.result), 1)
            self.server.exit()
            return
        # 进入monitor文件夹
        self.server.exec_cmd(['cd %s\n' % SERVER_WORK_FILENAME])
        monitor_process_id_list = []
        for java_process_id in java_process_id_list:
            # 根据场景信息、进程id定义监控结果文件名称
            file_name = './mon_result/%s/%s_%s_%s_%s.gc' % (
                self.file_path, self.ip, self.scene_name, self.timestamp, java_process_id)
            # gc监控采集间隔单位为毫秒，据场景设置间隔*1000
            scene_step = self.scene_step * 1000
            # 将监控时长保存到监控结果文件中
            self.server.exec_cmd(['echo \'%s\'>%s\n' % (self.scene_times * self.scene_step, file_name)])
            # 生成监控命令
            process_monitor_command = 'nohup jstat -gcutil {process_id} {scene_step} {scene_times} >>{file} 2>/dev/null &\n'.format(
                process_id=java_process_id, scene_step=scene_step, scene_times=self.scene_times, file=file_name)
            self.server.exec_cmd([process_monitor_command])
            # 响应结果及获取末尾进程id方法
            # '''nohup jstat -gcutil 9366 3000 3 &
            #     [1] 9837'''
            monitor_process_id = self.server.result.strip().split()[-1].split()[-1]
            monitor_process_id_list.append(monitor_process_id)
        # 执行检查监控进程命令
        check_monitor_process_command = ['ps -ef |grep jstat|grep -v \'grep\'|awk \'{print $2}\'\n']
        self.server.exec_cmd(check_monitor_process_command)
        logger.debug("up monitor process\n" + self.server.result)
        # 监控进程数
        all_monitor_process_id_list = self.server.result.strip().split('\n')[1:]
        all_monitor_process_id_list = [x.strip() for x in all_monitor_process_id_list]
        # 监控进程数与Java进程数相同，则启动监控成功，否则启动失败
        if set(monitor_process_id_list) <= set(all_monitor_process_id_list):
            show_monitor_process_info_command = ['ps -ef |grep jstat|grep -v \'grep\'\n']
            self.server.exec_cmd(show_monitor_process_info_command)
            with self.lock:
                self.root.set_monitor_log('%s\nGC监控启动成功！\n%s\n' % (self.ip, self.server.result))
            self.tag = 1
        else:
            with self.lock:
                self.root.set_monitor_log('%s\nGC监控启动失败！\n%s\n' % (self.ip, self.server.result), 1)
        self.server.exit()
