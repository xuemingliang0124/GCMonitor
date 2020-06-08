import configparser
import logging
import os
import re
import time
import zipfile


# 若配置文件不存在，则生成
def init_config():
    conf_path = 'Resource_Monitor.conf'
    cf = configparser.ConfigParser()
    if os.path.exists(conf_path):
        pass
    else:
        conf = {'PATH':
                    {'workspace': '',
                     'version_check_path': '/XMON/VersionCheck'},
                'LOG':
                    {'LogLevel': 'DEBUG',
                     'FileSize': '2',
                     'LogPath': 'log/resource_result.log'}}
        for sec, opts in conf.items():
            cf.add_section(sec)
            for opt, value in opts.items():
                cf.set(section=sec, option=opt, value=value)
        with open(conf_path, 'w', encoding='utf-8-sig') as f:
            cf.write(f)

    # 读取日志配置信息
    cf.read(conf_path, encoding='utf-8-sig')
    loglevel = cf.get('LOG', 'LogLevel')
    filesize = cf.get('LOG', 'FileSize')
    log_path = cf.get('LOG', 'LogPath')
    version_checkpath = cf.get('PATH', 'version_check_path')

    # 日志打包、上传
    def handle_log():
        if os.path.exists(log_path):
            size = os.path.getsize(log_path) / 1024 / 1024
            if size >= float(filesize):
                a = os.popen('ipconfig /all')
                b = a.read()
                str = re.compile(r'(?ims): (\d+\.\d+\.\d+\.\d+)\(')
                result = str.search(b)
                name = result.group(1) if result else None
                stamp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                source = log_path
                sourcename = source.split('/')[-1]
                zipname = 'log\\%s_%s_resource_result.zip' % (name, stamp)
                zip = zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED)
                zip.write(source, sourcename)
                zip.close()
        else:
            os.makedirs('log')

    handle_log()

    # 日志设置
    logger = logging.getLogger('JvmMonitor')
    logger.setLevel(level=eval('logging.%s' % loglevel))

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s')

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
