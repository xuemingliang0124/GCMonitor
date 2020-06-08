import logging
import time

from publick_class.execute import Execute

logger = logging.getLogger('XMON.Step_route.RunMonitor')


class JvmMonitor(Execute):
    def __init__(self, *args):
        super().__init__(*args)
        self.create_time()
        self.create_filepath()
        self.upmonitor()
        self.execute_date = ''
        self.execute_time = ''

    def create_time(self):
        times = self.timestamp
        self.execute_date = str(time.strftime('%Y%m%d', times))
        self.execute_time = str(time.strftime('%Y%m%d%H%M', times))

    def create_filepath(self):
        path = './monitor/mon_result/%s' % self.execute_date
        command = ['mkdir -p %s\n' % path]
        self.server.exec_cmd(command)
        for i in self.error_str:
            if i.lower() not in self.server.result.lower():
                pass
            else:
                self.root.set_res('%s\n创建文件夹失败！\n%s' % (self.ip, self.server.result))
                self.server.exit()
                exit(0)
        self.result_path = path

    def upmonitor(self):
        # 查询java进程
        find_java_process_id_command = ['ps -ef |grep java|grep -v \'grep\'|awk \'{print $2}\'\n']
        self.server.exec_cmd(find_java_process_id_command)
        # 判断是否存在Java进程，不存在直接结束
        java_process_id_list = self.server.result.strip().split('\n')[1:]
        if len(java_process_id_list) < 1:
            with self.lock:
                self.root.set_res(
                    '%s\n%s启动失败，没有找到Java进程！\n%s\n\n\n' % (self.ip, self.server.monitor, self.server.result), 1)
            self.server.exit()
            return
        # 进入monitor文件夹
        self.server.exec_cmd(['cd monitor\n'])
        up_command_list = []
        monitor_process_id_list = []
        for java_process_id in java_process_id_list:
            # 根据场景信息、进程id定义监控结果文件名称
            file_name = './mon_result/%s/%s_%s_%s_%s.gc' % (
                self.execute_date, self.ip, self.scene_name, self.execute_time, java_process_id)
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
        # 监控进程数
        all_monitor_process_id_list = self.server.result.strip().split('\n')[1:]
        all_monitor_process_id_list = [x.strip() for x in all_monitor_process_id_list]
        # 监控进程数与Java进程数相同，则启动监控成功，否则启动失败
        if set(monitor_process_id_list) <= set(all_monitor_process_id_list):
            with self.lock:
                self.root.set_res('%s\nGC监控启动成功！\n%s\n\n\n' % (self.ip, self.server.result))
            self.tag = 1
        else:
            with self.lock:
                self.root.set_res('%s\nGC监控启动失败！\n%s\n\n\n' % (self.ip, self.server.result), 1)
        self.server.exit()
