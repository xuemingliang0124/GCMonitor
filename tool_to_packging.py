import os
from public_class.src_to_exe_to_zip import Packaging
from public_class.threads_control import MyThread

path = os.getcwd().split('\\jvm_monitor_git')[0]

distpath = os.path.join(path, 'dist')
workpath = os.path.join(distpath, 'build')
mainfile_path = os.path.join(path, 'jvm_monitor_git\\main.py')
zip_to_path = os.path.join(distpath, 'GCMonitor')
venv_path = r'D:\PycharmProjects\venv\Scripts\activate'
command = 'pyinstaller -F -w -y %s -n GC分布式监控工具 --distpath %s --workpath %s' % (mainfile_path, distpath, workpath)
print(command)
pack = Packaging()
pack_thread = MyThread(pack.src_to_exe, (workpath, distpath, command), 'packing')
pack_thread.start()
pack_thread.join()
# pack.src_to_exe(workpath, distpath, command, venv_path)
# zip_thread = pack_thread = MyThread(pack.exe_to_zip, (zip_to_path, 'GCMonitor.zip'), 'zipping')
# zip_thread.start()
# zip_thread.join()
# pack.exe_to_zip(zip_to_path, 'GCMonitor.zip')
