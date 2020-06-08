import configparser
import os
import tkinter.messagebox as tkMessageBox
import winreg
from publick_class.service_connector import myTrans
from publick_class import SFTPConfig


def VersionCheck(Version, Tools):
    server = myTrans(SFTPConfig.ip, SFTPConfig.port, SFTPConfig.uname, SFTPConfig.passwd)
    remotepath = os.path.join(SFTPConfig.server_path, 'XMON/VersionCheck/Version.txt')
    server.download('Version.txt', remotepath)
    cf = configparser.ConfigParser()
    cf.read('./Version.txt')
    new_version = cf.get('VERSION', Tools)
    if float(Version[1:]) < float(new_version[1:]):
        if tkMessageBox.askyesno('通知', '检查到有新版本，最新版本为：%s,是否下载？' % new_version):
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r'Software\Microsoft\Windows\CurrentVersion\Expolrer\Shell Folders')
            localpath = os.path.join(winreg.QueryValueEx(key, 'Desktop')[0], '%s_%s.zip' % (Tools, new_version))
            remotepath = '/XiaoGongJu/{Tool}/{Version}/{Tool}_{Version}.zip'.format(Tool=Tools, Version=new_version)
            try:
                server.download(localpath, remotepath)
                result = localpath
                tkMessageBox.showinfo('下载成功！', '下载成功,保存在%s!' % result)
            except:
                tkMessageBox.showinfo('下载失败！', '下载失败！')
