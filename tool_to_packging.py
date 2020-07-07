import os
from publick_class.src_to_exe_to_zip import Packaging

path = os.getcwd().split('\\jvm_monitor_git')[0]

distpath = os.path.join(path, 'dist')
workpath = os.path.join(distpath, 'build')
mainfile_path = os.path.join(path, 'jvm_monitor_git\\main.py')
zip_to_path = os.path.join(distpath, 'GCMonitor')
command = 'pyinstaller -F -w -y %s -n GCMonitor --distpath %s --workpath %s' % (mainfile_path, distpath, workpath)
print(command)
pack = Packaging()
pack.src_to_exe(workpath, distpath, command)
pack.exe_to_zip(zip_to_path, 'GCMonitor.zip')
