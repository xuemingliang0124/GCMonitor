from PyQt5 import QtWidgets


class StandardMessageBox(QtWidgets.QMessageBox):
    def __init__(self, parent: QtWidgets, title: str, content: str, button_1='确认', button_2='',
                 type=QtWidgets.QMessageBox.Warning, auto_show=True):
        super().__init__(parent)
        self.setStyleSheet("font: 10pt \"微软雅黑\";")
        self.setWindowTitle(title)
        self.setText(content)
        self.setIcon(type)
        if button_1:
            self.addButton(button_1, QtWidgets.QMessageBox.YesRole)
        if button_2:
            self.addButton(button_2, QtWidgets.QMessageBox.NoRole)
        if auto_show:
            self.show_dialog()

    def show_dialog(self):
        return self.exec()


class StardardQInputDialog(QtWidgets.QInputDialog):
    def __init__(self, *args):
        super().__init__(*args)
        self.setStyleSheet("font: 12pt \"微软雅黑\";")
