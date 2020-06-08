import os
import shutil
import time
import zipfile


class Packaging:
    @staticmethod
    def src_to_exe(work_path, dist_path, command, python_path=r'C:\Python36-32'):
        env = os.environ['path']
        temp = env.split(';')
        env_list = temp[:]
        for i, env_value in enumerate(temp):
            if 'python' in env_value.lower():
                env_list.remove(env_value)
        env_list.append(python_path)
        env_list.append(os.path.join(python_path, 'Scripts'))
        env_list.append(os.path.join(python_path, 'lib\site-packages\pywin32_system32'))
        os.environ['path'] = ';'.join(env_list)
        if os.path.exists(dist_path):
            shutil.rmtree(dist_path)
            time.sleep(2)
            os.makedirs(work_path)
        os.system(command)

    @staticmethod
    def exe_to_zip(self, path, zip_name):
        zip_path = '\\'.join(path.split('\\')[:-1])
        zip = zipfile.ZipFile(os.path.join(zip_path, zip_name), 'w', zipfile.ZIP_DEFLATED)
        pre_len=len(os.path.dirname(path))
        for parent,dirnames,filenames in os.walk(path):
            for filename in filenames:
                print(filename)
                path_file=os.path.join(parent,filename)
                arcname=path_file[pre_len:].strip(os.path.sep)
                zip.write(path_file,arcname)
        zip.close()