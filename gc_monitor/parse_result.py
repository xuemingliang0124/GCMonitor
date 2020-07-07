import datetime
import logging
import os
import pandas as pd
from PyQt5.QtWidgets import QMessageBox
import re
import sys

from public_class.threads_control import MyThread
from decorators import output_log
from gc_monitor_ui.standard_components import StandardMessageBox

logger = logging.getLogger('GCMonitor.UI.StepRoute.ParseResult')


class ParseResult:
    def __init__(self, local_result_path, result_name, root):
        self.local_result_path = local_result_path
        self.analysis_file_name = result_name
        self.monitor_result_path = ''
        self.analysis_file_path = ''
        self.root = root
        self.cols_name = []
        for i in range(1, 27):
            self.cols_name.append(chr(i - 1 + ord('A')))
        self.reg_str = re.compile(r'((.*?)_|)(\d+\.\d+\.\d+\.\d+)_(.+_\d+)_(\d*?).(gc)')
        self.parse_result()

    @output_log("ParseResult", logger)
    def parse_result(self):
        # 获取结果文件夹下所有gc监控结果文件名
        filename_list = self.get_filename_list()
        # 结果对应ip
        ip_list = []
        # 监控java进程id
        java_process_id_list = []
        # YGC次数(次)
        ygc_times_list = []
        # YGC总时长（毫秒）
        ygc_total_duration_list = []
        # YGC频率（次/秒）
        ygc_frequency_list = []
        # YGC平均时长（毫秒）
        ygc_average_duration_list = []
        # FGC次数（次）
        fgc_times_list = []
        # FGC总时长（毫秒）
        fgc_total_duration_list = []
        # FGC频率（次/秒）
        fgc_frequency_list = []
        # FGC平均时长（毫秒）
        fgc_average_duration_list = []
        # 详细结果数据集
        detail_result_dataframe_list = []
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
            # 监控期间ygc次数
            ygc_times_during_monitor = monitor_dataframe['YGC'].tolist()
            ygc_times_during_monitor = ygc_times_during_monitor[-1] - ygc_times_during_monitor[0]
            ygc_times_list.append(ygc_times_during_monitor)
            # 监控期间ygc总时长
            ygc_total_duration = monitor_dataframe['YGCT'].tolist()
            ygc_total_duration = ygc_total_duration[-1] - ygc_total_duration[0]
            ygc_total_duration_list.append(ygc_total_duration)
            # 监控期间ygc频率
            ygc_frequency = ygc_times_during_monitor / monitor_time if monitor_time > 0 else 0
            ygc_frequency_list.append(ygc_frequency)
            # 监控期间ygc平均时长
            ygc_average_duration = ygc_total_duration / ygc_times_during_monitor if ygc_times_during_monitor else 0
            ygc_average_duration_list.append(ygc_average_duration)
            # 监控期间fgc次数
            fgc_times_during_monitor = monitor_dataframe['FGC'].tolist()
            fgc_times_during_monitor = fgc_times_during_monitor[-1] - fgc_times_during_monitor[0]
            fgc_times_list.append(fgc_times_during_monitor)
            # 监控期间fgc总时长
            fgc_total_duration = monitor_dataframe['YGCT'].tolist()
            fgc_total_duration = fgc_total_duration[-1] - fgc_total_duration[0]
            fgc_total_duration_list.append(fgc_total_duration)
            # 监控期间fgc频率
            fgc_frequency = fgc_times_during_monitor / monitor_time if monitor_time > 0 else 0
            fgc_frequency_list.append(fgc_frequency)
            # 监控期间fgc平均时长
            fgc_average_duration = fgc_total_duration / fgc_times_during_monitor if fgc_times_during_monitor else 0
            fgc_average_duration_list.append(fgc_average_duration)
            # 筛选数据
            detail_result_dataframe = monitor_dataframe.loc[:, 'S0':'M']
            # 添加序号
            detail_result_dataframe.insert(0, '采样次数', range(1, len(monitor_dataframe) + 1))
            detail_result_data_rows = len(detail_result_dataframe)
            detail_result_dataframe_list.append(
                {"detail_result_dataframe": detail_result_dataframe, "sheet_name": sheet_name,
                 "detail_result_data_rows": detail_result_data_rows,
                 "monitor_start_time": monitor_start_time,
                 "service_ip": monitor_service_ip, "process_id": monitor_process_id})
        # 概要结果数据集
        summary_monitor_dataframe = {'IP地址': ip_list, 'Java进程ID': java_process_id_list, 'YGC次数(次)': ygc_times_list,
                                     'YGC总时长（毫秒）': ygc_total_duration_list, 'YGC频率（次/秒）': ygc_frequency_list,
                                     'YGC平均时长（毫秒）': ygc_average_duration_list, 'FGC次数（次）': fgc_times_list,
                                     'FGC总时长（毫秒）': fgc_total_duration_list, 'FGC频率（次/秒）': fgc_frequency_list,
                                     'FGC平均时长（毫秒）': fgc_average_duration_list}
        summary_monitor_dataframe = pd.DataFrame(summary_monitor_dataframe)
        summary_monitor_dataframe.to_excel(analysis_result_file_writer, index=False, sheet_name='监控结果概要')
        summary_sheet = analysis_result_file_writer.sheets["监控结果概要"]
        for index, key in enumerate(summary_monitor_dataframe.keys()):
            summary_sheet.set_column(index, index + 1, width=len(key) * 1.89)
        for result_info in detail_result_dataframe_list:
            detail_result_dataframe = result_info["detail_result_dataframe"]
            sheet_name = result_info["sheet_name"]
            detail_result_dataframe.to_excel(analysis_result_file_writer, index=False, sheet_name=sheet_name)
            self.create_chart(analysis_result_file_writer, result_info)
        try:
            analysis_result_file_writer.save()
        except:
            logger.exception(sys.exc_info())
            self.root.set_monitor_log('%s已打开，请关闭重试！\n' % self.analysis_file_path, 1)
            return
        os.remove('temp.csv')
        question_str = "监控分析完成，是否打开？"
        try:
            question_dialog = StandardMessageBox(self.root.MainWindow, '结果解析', question_str, '确认', '取消',
                                                 QMessageBox.Question)
            if question_dialog.clickedButton().text() == '确认':
                MyThread(os.system, (self.analysis_file_path,), 'open analysis').start()
                self.root.set_monitor_log('监控结果已打开，保存位置%s\n' % self.analysis_file_path)
            else:
                self.root.set_monitor_log('监控结果分析完成，保存位置%s\n' % self.analysis_file_path)
        except:
            logger.exception(sys.exc_info())

    @output_log("GetFilenameList", logger)
    def get_filename_list(self):
        self.analysis_file_path = os.path.join(self.local_result_path, 'GC_' + self.analysis_file_name + '.xlsx')
        self.analysis_file_path = self.analysis_file_path.replace('/', '\\')
        filename_list = os.listdir(self.local_result_path)
        filename_list = filter(lambda x: x.endswith('.gc'), filename_list)
        return filename_list

    @output_log("CreateChart", logger)
    def create_chart(self, excel_writer: pd.ExcelWriter, result_info: dict):
        monitor_start_time = result_info["monitor_start_time"]
        monitor_start_time = datetime.datetime.strptime(monitor_start_time, "%Y%m%d%H%M%S")
        sheet_name = result_info["sheet_name"]
        monitor_data_rows = result_info["detail_result_data_rows"]
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
