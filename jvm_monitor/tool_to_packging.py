from publick_class.src_to_exe_to_zip import Packaging
from publick_class import VersionConfig

Version = VersionConfig.XMON_Version
workpath = r'D:\workspace\py3\dist\XMON_dist\build'
distpath = r'D:\workspace\py3\dist\XMON_dist'
zip_to_path = r'D:\workspace\py3\dist\XMON_dist\XMON_%s' % Version
command = 'pyinstaller -D -w -y jvm_monitor_main_gui.py -n XMON_%s --distpath %s --workpath %s' % (
    Version, distpath, workpath
)
pack = Packaging()
pack.src_to_exe(workpath, distpath, command)
pack.exe_to_zip(zip_to_path, 'XMON_%s.zip' % Version)
