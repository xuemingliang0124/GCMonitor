from tkinter import messagebox
import logging
import os
import pandas as pd
import re
import sys
import datetime

sys.path.append('..')

from publick_class.threads_control import MyThread

logger = logging.getLogger('XMON.Step_route.ParseResult')


class ParseResult:
    def __init__(self, local_result_path, result_name, root):
        try:
            self.local_result_path = local_result_path.decode('utf8')
        except:
            self.local_result_path = local_result_path
        self.analysis_file_name = result_name[0]
        self.monitor_result_path = ''
        self.analysis_file_path = ''
        self.root = root
        self.cols_name = []
        for i in range(1, 27):
            self.cols_name.append(chr(i - 1 + ord('A')))
        self.reg_str = re.compile(r'((.*?)_|)(\d+\.\d+\.\d+\.\d+)_(.+_\d+)_(\d*?).(gc)')
        self.parse_result()

    def parse_result(self):
        # 获取结果文件夹下所有gc监控结果文件名
        filename_list = self.get_filename_list()
        # 每项监控的总体结果及所有监控的详细结果
        ip_list = []
        java_process_id_list = []
        gc_times_list = []
        gc_frequency_list = []
        gc_time_list = []
        monitor_dataframe_list = []
        analysis_result_file_writer = pd.ExcelWriter(self.analysis_file_path)
        for monitor_result_file in filename_list:
            # 拼接监控结果路径+监控结果文件名
            monitor_file_path = os.path.join(self.local_result_path, monitor_result_file)
            # 正则匹配文件名，获取被监控服务器ip及被监控java进程id
            monitor_file_regular_result = self.reg_str.search(monitor_result_file)
            # 结果文件对应服务器ip
            monitor_service_ip = monitor_file_regular_result.group(3)
            # 结果文件监控开始时间
            monitor_start_time = monitor_file_regular_result.group(4)
            monitor_start_time = monitor_start_time.split("_")[-1]
            # 结果文件对应进程id
            monitor_process_id = monitor_file_regular_result.group(5)
            ip_list.append(monitor_service_ip)
            java_process_id_list.append(monitor_process_id)
            # sheet页名称为服务器ip_Java进程id
            sheet_name = '%s_%s' % (monitor_service_ip, monitor_process_id)
            # 监控结果文件首行为场景执行时长，移除该项并生成新的csv文件
            with open(monitor_file_path, 'r', encoding='utf8') as f:
                lines = f.readlines()
                monitor_time = int(lines[0].strip())
            with open('temp.csv', 'w', encoding='utf8') as f:
                f.write(''.join(lines[1:]))
            # 将监控结果数据读取为pandas数据对象
            monitor_dataframe = pd.read_csv('temp.csv', sep='\s+')
            gc_times_during_monitor = monitor_dataframe['FGC'].tolist()
            # 监控期间full gc次数
            gc_times_during_monitor = gc_times_during_monitor[-1] - gc_times_during_monitor[0]
            gc_times_list.append(gc_times_during_monitor)
            # 监控期间gc频率
            gc_frequency = gc_times_during_monitor / monitor_time if monitor_time > 0 else 0
            gc_frequency_list.append(gc_frequency)
            # 监控期间full gc持续时间
            gc_time_during_monitor = monitor_dataframe['FGCT'].tolist()
            gc_time_during_monitor = gc_time_during_monitor[-1] - gc_time_during_monitor[0]
            gc_time_list.append(gc_time_during_monitor)
            # 筛选数据
            monitor_dataframe = monitor_dataframe.loc[:, 'S0':'M']
            # 添加序号
            monitor_dataframe.insert(0, '采样次数', range(1, len(monitor_dataframe) + 1))
            monitor_data_rows = len(monitor_dataframe)
            monitor_dataframe_list.append({"monitor_dataframe": monitor_dataframe, "sheet_name": sheet_name,
                                           "monitor_data_rows": monitor_data_rows,
                                           "monitor_start_time": monitor_start_time,
                                           "service_ip": monitor_service_ip, "process_id": monitor_process_id})
        all_monitor_result = {'IP地址': ip_list, 'Java进程ID': java_process_id_list, 'GC次数': gc_times_list,
                              'GC频率': gc_frequency_list, 'GC持续时长': gc_time_list}
        summary_monitor_dataframe = pd.DataFrame(all_monitor_result)
        summary_monitor_dataframe.to_excel(analysis_result_file_writer, index=False, sheet_name='监控结果概要')
        summary_sheet = analysis_result_file_writer.sheets["监控结果概要"]
        summary_sheet.set_column('A:E', 16)
        for result_info in monitor_dataframe_list:
            monitor_dataframe = result_info["monitor_dataframe"]
            sheet_name = result_info["sheet_name"]
            monitor_dataframe.to_excel(analysis_result_file_writer, index=False, sheet_name=sheet_name)
            self.create_chart(analysis_result_file_writer, result_info)
        try:
            analysis_result_file_writer.save()
        except:
            self.root.set_res('%s已打开，请关闭重试！\n\n\n' % self.analysis_file_path, 1)
            return
        os.remove('temp.csv')
        if messagebox.askyesno(title='结果解析', message='监控分析完成，是否打开？'):
            MyThread(os.system, (self.analysis_file_path,), 'open analysis').start()
            self.root.set_res('监控结果已打开，保存位置%s\n\n\n' % self.analysis_file_path)
        else:
            self.root.set_res('监控结果分析完成，保存位置%s\n\n\n' % self.analysis_file_path)

    def get_filename_list(self):
        monitor_file_regular_result = self.reg_str.search(self.analysis_file_name)
        if monitor_file_regular_result:
            self.analysis_file_name = monitor_file_regular_result.group(4)
        else:
            self.root.set_res('\n解析失败\n%s\n' % self.analysis_file_name, 1)
            sys.exit()
        self.analysis_file_path = os.path.join(self.local_result_path, 'GC_' + self.analysis_file_name + '.xlsx')
        self.analysis_file_path = self.analysis_file_path.replace('/', '\\')
        filename_list = os.listdir(self.local_result_path[:])
        filename_list = list(filter(lambda x: x.endswith('.gc'), filename_list))
        return filename_list

    def create_chart(self, excel_writer: pd.ExcelWriter, result_info: dict):
        monitor_start_time = result_info["monitor_start_time"]
        monitor_start_time = datetime.datetime.strptime(monitor_start_time, "%Y%m%d%H%M%S")
        sheet_name = result_info["sheet_name"]
        monitor_data_rows = result_info["monitor_data_rows"]
        service_ip = result_info["service_ip"]
        process_id = result_info["process_id"]
        workbook = excel_writer.book
        worksheet = excel_writer.sheets[sheet_name]
        chart = workbook.add_chart({'type': 'line'})
        for i in range(5):
            col = i + 1
            chart.add_series({
                'name': [sheet_name, 0, col],
                'categories': [sheet_name, 1, 0, monitor_data_rows, 0],
                'values': [sheet_name, 1, col, monitor_data_rows, col]
            })
        chart.set_x_axis({'name': '执行时间：%s' % monitor_start_time})
        chart.set_y_axis({'name': '内存百分比（%）', 'major_girdlines': {'visible': False}, 'max': 100})
        chart.set_title({"name": "%s_%s" % (service_ip, process_id)})
        chart.width = 13 * 60
        chart.height = 20 * 24
        worksheet.insert_chart('H2:T25', chart)
