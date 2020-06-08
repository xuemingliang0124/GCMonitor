import os
import shutil


def cleardirectory():
    path_list = ['./XMON', './VERCHK', './Tuxedo_monitor', './CONFIGCHK']
    for path in path_list:
        for i in os.listdir(path):
            filepath = os.path.join(path, i)
            if not i.endswith('.py'):
                if os.path.isfile(filepath):
                    os.remove(filepath)
                elif os.path.isdir(filepath):
                    shutil.rmtree(filepath)


if __name__ == '__main__':
    cleardirectory()
