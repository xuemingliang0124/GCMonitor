import configparser
import logging
import os

from global_var import CONFIG_FILE


# 若配置文件不存在，则生成
def init_config():
    cf = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        pass
    else:
        conf = {'PATH':
                    {'workspace': '',
                     'services_list_file': ''},
                'LOG':
                    {'LogLevel': 'DEBUG',
                     'FileSize': '2',
                     'LogPath': 'GCMonitor.log'},
                'PROJECTS':
                    {}}
        for sec, opts in conf.items():
            cf.add_section(sec)
            for opt, value in opts.items():
                cf.set(section=sec, option=opt, value=value)
        with open(CONFIG_FILE, 'w', encoding='utf-8-sig') as f:
            cf.write(f)

    # 读取日志配置信息
    cf.read(CONFIG_FILE, encoding='utf-8-sig')
    loglevel = cf.get('LOG', 'LogLevel')
    filesize = cf.get('LOG', 'FileSize')
    log_path = cf.get('LOG', 'LogPath')

    # 日志打包、上传
    def handle_log():
        if os.path.exists(log_path):
            size = os.path.getsize(log_path) / 1024 / 1024
            if size < float(filesize):
                return
        with open(log_path, 'w', encoding='utf8') as f:
            pass

    handle_log()

    # 日志设置
    logger = logging.getLogger('GCMonitor')
    logger.setLevel(level=eval('logging.%s' % loglevel))

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s')

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
