from PyQt5 import QtCore

from gc_monitor_ui import jvm_main
from gc_monitor.step_route import StepRoute
from public_class.threads_control import MyThread
from gc_monitor_ui.standard_components import StardardQInputDialog
from decorators import *

logger = logging.getLogger("GCMonitor.UI")


class UIAfterBindEvent(jvm_main.Ui_GCMonitor):
    def __init__(self, MainWindow, app):
        super().__init__()
        self.MainWindow = MainWindow
        self.app = app
        self.placeholder = "<font color=\"#cfcfcf\">" + "127.0.0.1:user:passwd" + "<font>"

    def setupEvent(self, MainWindow):
        self.hide_confirm_download_frame()
        y = self.operation_subframe_3.y()
        x = self.operation_subframe_3.x()
        self.operation_subframe_3.move(x, y - 81)
        self.retranslateUi(MainWindow)
        self.menu_version.triggered.connect(self.show_version_dialog)
        self.btn_workspace_scan.clicked.connect(self.ask_workspace_path)
        self.btn_services_info_scan.clicked.connect(self.ask_services_info_path)
        self.btn_init_env.clicked.connect(self.init_environment)
        self.btn_run_monitor.clicked.connect(self.run_monitor)
        self.btn_download.clicked.connect(self.show_confirm_download_frame)
        self.btn_stop_monitor.clicked.connect(self.kill_monitor)
        self.btn_clear_monitor.clicked.connect(self.clear_service)
        self.btn_confirm_download.clicked.connect(self.download_monitor_result)
        self.btn_cancel_download.clicked.connect(self.hide_confirm_download_frame)
        self.btn_clear_local_records.clicked.connect(self.clear_local_records)
        self.btn_services_edit.clicked.connect(self.change_services_text_status)
        self.comb_scene_time.currentTextChanged.connect(self.set_scene_times)
        self.comb_scene_step.currentTextChanged.connect(self.set_scene_times)
        self.text_services_info.setPlaceholderText("127.0.0.1:user:passwd")
        self.comb_scene_time.setCurrentText("12小时")
        self.comb_scene_step.setCurrentText("60秒")
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def setupPath(self):
        self.check_workspace()
        self.check_ip_list_path()

    def ask_services_info_path(self):
        services_info_path, file_type = QtWidgets.QFileDialog.getOpenFileName(self.services_set_frame, "选择服务器列表文", "./",
                                                                              "Text Files (*.txt)")
        if services_info_path:
            self.entry_services_info_path.setText(services_info_path)
            self.read_services_file()
            self.save_services_info_filepath(services_info_path)

    def ask_workspace_path(self):
        workspace_path = QtWidgets.QFileDialog.getExistingDirectory(self.workspace_set_frame, "选择工作区路径", "./")
        if workspace_path:
            self.entry_workspace_path.setText(workspace_path)
            self.save_workspace_path(workspace_path)

    def change_services_status(self):
        pass

    def check_ip_list_path(self):
        if os.path.exists(CONFIG_FILE):
            cf = configparser.ConfigParser()
            cf.read(CONFIG_FILE, encoding='utf-8-sig')
            self.entry_services_info_path.setText(cf.get(section='PATH', option='services_list_file'))
            self.read_services_file()

    def check_workspace(self):
        if os.path.exists(CONFIG_FILE):
            cf = configparser.ConfigParser()
            cf.read(CONFIG_FILE, encoding='utf-8-sig')
            self.entry_workspace_path.setText(cf.get(section='PATH', option='workspace'))

    @check_monitor_status
    def clear_local_records(self, *args):
        str_1 = "<font color=\"red\">" + "本地执行记录" + "</font>"
        str_2 = "<font color=\"red\">" + "不会影响" + "</font>"
        warn_str = '此操作将清除%s，%s服务器保存结果，清除后服务器结果只能手动下载，是否继续？\n\n（如需清理服务器结果，请执行清理服务器操作。）'
        clear_local_records_dialog = StandardMessageBox(self.MainWindow, '警告！', warn_str % (str_1, str_2), '确认', '取消',
                                                        QtWidgets.QMessageBox.Question)
        if clear_local_records_dialog.clickedButton().text() == '确认':
            self.clear_projects_status()
            with open(MONITOR_RECORD, 'w', encoding='utf8') as f:
                pass
            self.update_monitor_record()
        else:
            self.set_monitor_log("操作取消！")

    def clear_monitor_log(self):
        self.text_operation_log.clear()

    def clear_projects_status(self):
        current_project = self.entry_services_info_path.text().replace(':', "|")
        cf = configparser.ConfigParser()
        cf.read(CONFIG_FILE, encoding='utf-8-sig')
        if current_project:
            project_status = cf.get('PROJECTS', current_project)
            cf.remove_section('PROJECTS')
            cf.add_section('PROJECTS')
            cf.set('PROJECTS', current_project, project_status)
        else:
            cf.remove_section('PROJECTS')
            cf.add_section('PROJECTS')
        with open(CONFIG_FILE, 'w', encoding='utf-8-sig') as f:
            cf.write(f)

    @check_project_status
    @check_monitor_status
    def clear_service(self, *args):
        warn_str = '此操作将永久删除服务器的jscsc_test_monitor文件夹及文件夹下所有内容，请谨慎操作！\n是否继续？'
        delete_dialog = StandardMessageBox(self.MainWindow, '警告！', warn_str, '确认', '取消', QtWidgets.QMessageBox.Question)
        if delete_dialog.clickedButton().text() == '确认':
            confirm_delete_dialog, confirm_ok = StardardQInputDialog.getText(self.MainWindow, '确认', '如确认删除，请输入“删除”')
            if confirm_ok:
                step = 'DeleteResult'
                self.execute_command(step)
            else:
                self.clear_monitor_log()
                self.set_monitor_log('操作取消！\n')
        else:
            # logger.debug('delete result cancel')
            self.clear_monitor_log()
            self.set_monitor_log('操作取消！\n')

    @check_workspace_path
    @check_project_status
    @check_download_monitor_status
    def download_monitor_result(self):
        scene_info_str = self.get_download_scene_info()
        scene_info_list = [x.strip() for x in scene_info_str.split('|')]
        scene_name, scene_date, status, scene_time = [x.split(':')[1] for x in scene_info_list]
        scene_info = {'scene_date': scene_date, 'scene_time': scene_time, 'scene_name': scene_name}
        step = 'DownLoadResult'
        self.execute_command(step, download_scene_info=scene_info)

    @check_ip_info
    @update_services_info
    def execute_command(self, step, download_scene_info=None):
        # 隐藏下载子控件
        self.hide_confirm_download_frame()
        # # 清除执行日志
        # self.clear_monitor_log()
        servers = self.format_services(self.text_services_info.toPlainText())
        run_scene_info = self.get_run_scene_info()
        result_save_path = self.entry_workspace_path.text()
        step_route = StepRoute(self, result_save_path, step, servers, run_scene_info, download_scene_info)
        MyThread(step_route.execute, (), step).start()

    def format_services(self, servers):
        temp = []
        servers = servers.strip().split("\n")
        for server in servers:
            server = server.replace("：", ":").split(":")
            temp.append({"ip": server[0], "port": 22, "uname": server[1], "passwd": server[2]})
        return temp

    def get_download_scene_info(self) -> str:
        download_combobox_selected_index = self.comb_monitor_history_list.currentIndex()
        with open(MONITOR_RECORD, 'r', encoding='utf8') as f:
            lines = f.readlines()
        if len(lines)==0:
            return '请选择监控结果:'
        download_combobox_selected_index = len(lines) - download_combobox_selected_index - 1
        scene_info_str = lines[download_combobox_selected_index]
        return scene_info_str

    def get_run_scene_info(self):
        return {'scene_name': self.entry_scene_name.text(),
                'scene_step': int(self.comb_scene_step.currentText().strip('秒')),
                'scene_times': int(self.lab_scene_times.text().strip('次')),
                'scene_time': int(self.comb_scene_time.currentText().strip('小时')) * 3600}

    def hide_confirm_download_frame(self):
        self.confirm_download_frame.setVisible(False)
        self.operation_subframe_3.setVisible(True)

    def init_environment(self):
        step = 'InitEnv'
        self.execute_command(step)

    @check_project_status
    @kill_monitor_confirm
    def kill_monitor(self, *args):
        step = 'killJstat'
        self.execute_command(step)

    def read_services_file(self):
        services_info_path = self.entry_services_info_path.text()
        if os.path.exists(services_info_path):
            with open(self.entry_services_info_path.text(), 'r') as f:
                content = f.read()
            self.text_services_info.setText(content)

    @check_project_status
    @check_monitor_status
    @check_scene_name
    def run_monitor(self, *args):
        step = 'runJvmMonitor'
        self.execute_command(step)

    def save_services_info_filepath(self, services_list_file_path: str):
        cf = configparser.ConfigParser()
        cf.read(CONFIG_FILE, encoding='utf-8-sig')
        cf.set('PATH', 'services_list_file', services_list_file_path)
        try:
            services_list_file_path = services_list_file_path.replace(':', '|')
            project_status = cf.get('PROJECTS', services_list_file_path)
        except configparser.NoOptionError:
            cf.set('PROJECTS', services_list_file_path, '0')
        with open(CONFIG_FILE, 'w', encoding='utf-8-sig') as f:
            cf.write(f)

    def save_workspace_path(self, workspace_path):
        cf = configparser.ConfigParser()
        cf.read(CONFIG_FILE, encoding='utf-8-sig')
        cf.set('PATH', 'workspace', workspace_path)
        with open(CONFIG_FILE, 'w', encoding='utf-8-sig') as f:
            cf.write(f)

    def set_scene_times(self):
        scene_time = int(self.comb_scene_time.currentText().strip('小时')) * 3600
        scene_step = int(self.comb_scene_step.currentText().strip('秒'))
        scene_times = scene_time // scene_step
        self.lab_scene_times.setText(str(scene_times) + '次')

    def set_monitor_log(self, content: str, tag=0):
        if tag:
            contents = content.split('\n')
            for line_content in contents:
                self.text_operation_log.append("<p style=\" color:#ff5500;\">" + line_content + '</p>')
                time.sleep(0.2)
        else:
            self.text_operation_log.append(content)
        self.cursor = self.text_operation_log.textCursor()
        self.text_operation_log.moveCursor(self.cursor.End)


    def set_project_status(self, status='0'):
        project = self.entry_services_info_path.text().replace(":", "|")
        cf = configparser.ConfigParser()
        cf.read(CONFIG_FILE, encoding='utf-8-sig')
        cf.set('PROJECTS', project, status)
        with open(CONFIG_FILE, 'w', encoding='utf-8-sig') as f:
            cf.write(f)

    def show_confirm_download_frame(self):
        self.confirm_download_frame.setVisible(True)
        self.operation_subframe_3.setVisible(False)
        # y = self.operation_subframe_3.y()
        # x = self.operation_subframe_3.x()
        # self.operation_subframe_3.move(x, y + 81)

    def show_version_dialog(self):
        version_info = "版本：V1.0\n作者：薛明亮\n日期：2020/06/03"
        StandardMessageBox(self.MainWindow, "版本信息", version_info, '确认', type=QtWidgets.QMessageBox.Information)

    def update_monitor_record(self):
        self.comb_monitor_history_list.clear()
        _translate = QtCore.QCoreApplication.translate
        if os.path.exists(MONITOR_RECORD):
            with open(MONITOR_RECORD, 'r', encoding='utf-8') as f:
                all_monitor_records = f.readlines()
            if all_monitor_records:
                all_monitor_records.reverse()
                all_monitor_records = ['|'.join(x.split("|")[:-1]).strip() for x in all_monitor_records]
                for index, monitor_record in enumerate(all_monitor_records):
                    self.comb_monitor_history_list.addItem("")
                    self.comb_monitor_history_list.setItemText(index, _translate("MainWindow", monitor_record))
                self.comb_monitor_history_list.setCurrentIndex(0)
                return True
        self.comb_monitor_history_list.addItem("")
        self.comb_monitor_history_list.setItemText(0, _translate("MainWindow", "请选择监控结果:"))
