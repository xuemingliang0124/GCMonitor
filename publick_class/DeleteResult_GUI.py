import tkinter.messagebox as tkMessageBox
from tkinter import simpledialog
import logging

logger=logging.getLogger('XMON.DeleteResult_GUI')

class DeleteResult_GUI():
    def __init__(self):
        pass
    def delete_result(self,gui):
        if tkMessageBox.askokcancel('警告!','此操作将永久删除服务器的mon_result文件夹下所有内容，请谨慎操作！\n是否继续？'):
            delete_dialog=simpledialog.askstring(title='确认',prompt='如确认删除，请输入“确认”')
            if delete_dialog=='删除':
                step='DeleteResult'
                logger.debug('delete result begin,step:%s'%step)
                gui._execute_command(step)
            else:
                logger.debug('delete result cancel')
                gui.del_res()
                gui.set_res('操作取消！\n')
        else:
            logger.debug('delete result cancel')
            gui.del_res()
            gui.set_res('操作取消！\n')