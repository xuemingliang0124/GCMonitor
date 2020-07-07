import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from gc_monitor_ui import ui_bind_event
from gc_monitor import operation_log

operation_log.init_config()

app = QApplication(sys.argv)

MainWindow = QMainWindow()
ui = ui_bind_event.UIAfterBindEvent(MainWindow, app)
ui.setupUi(MainWindow)
ui.setupEvent(MainWindow)
ui.setupPath()
ui.update_monitor_record()

MainWindow.show()
sys.exit(app.exec_())

# '''监控执行状态：0-执行中，1-已完成，2-已终止，3-启动异常'''
# '''项目初始化状态（GCMonitor中PROJECTS下对应服务器列表路径） 0-未初始化，1-已初始化'''
