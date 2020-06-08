from functools import wraps
import os
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox

def syspathcheck(func):
    @wraps(func)
    def wrapped_function(*args):
        syspath = args[0].result_save_path.get()
        if syspath:
            if os.path.isfile(syspath):
                tkMessageBox.showinfo(title='', message='工作路径不应包含文件名，请重新设置！')
            elif not os.path.exists(syspath):
                tkMessageBox.showinfo(title='', message='没有找到{syspath}，请检查工作路径设置！'.format(syspath=syspath))
            else:
                return func(*args)
        else:
            tkMessageBox.showinfo(title='', message='请先设置工作路径，用于保存iplist及监控结果等文件')

    return wrapped_function

def ippathcheck(func):
    @wraps(func)
    def wrapped_function(*args):
        syspath = args[0].syspath_var.get()
        for i in os.listdir(syspath):
            if i == 'iplist.xlsx':
                args[0].iplist_path = os.path.join(syspath, i)
                return func(*args)
        else:
            args[0].set_res('没有找到"{syspath}/iplist.xlsx",请检查工作路径或先点击生成iplist模板并配置服务器ip信息!\n'.format(syspath=syspath))

    return wrapped_function