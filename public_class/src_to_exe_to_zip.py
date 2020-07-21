import os
import shutil
import time
import zipfile


class Packaging:
    @staticmethod
    def src_to_exe(work_path, dist_path, command: str):
        if os.path.exists(dist_path):
            shutil.rmtree(dist_path)
            time.sleep(2)
            os.makedirs(work_path)
            os.chdir(work_path)
        pack = os.popen(command)
        pack.read()

    @staticmethod
    def exe_to_zip(path, zip_name):
        zip_path = '\\'.join(path.split('\\')[:-1])
        zip = zipfile.ZipFile(os.path.join(zip_path, zip_name), 'w', zipfile.ZIP_DEFLATED)
        pre_len = len(os.path.dirname(path))
        for parent, dirnames, filenames in os.walk(path):
            for filename in filenames:
                print(filename)
                path_file = os.path.join(parent, filename)
                arcname = path_file[pre_len:].strip(os.path.sep)
                zip.write(path_file, arcname)
        zip.close()
