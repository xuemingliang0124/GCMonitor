import logging
import os
import sys
import xlrd
import xlsxwriter

logger = logging.getLogger('XMON.Iplist')


class IpList():
    def __init__(self, paths, root=None):
        self.paths = os.path.join(paths, 'iplist.xlsx')
        self.gui_obj = root

    def file_init(self):
        test_list = [['ip', '例：127.0.0.1'], ['prot', 'ssh连接所需端口，默认为22'], ['username', '服务器登陆用户，例：root'],
                     ['password', '服务器登陆密码，例：password'],
                     ['是否rac架构', '是（Y/y）或否（N/n）'], ['中间件类型', '请填写T（Tuxedo）/W（Weblogic）/N(无)']]
        excefile = xlsxwriter.Workbook(self.paths)
        logging.debug('iplist init,excefile:%s' % excefile)
        ws = excefile.add_worksheet('sheet1')
        for i, value in enumerate(test_list):
            ws.write(0, i, value[0])
            ws.write(1, i, value[1])
        try:
            excefile.close()
            self.gui_obj.del_res()
            logger.debug('iplist init,paths:%s' % self.paths)
            self.gui_obj.set_res('iplist.xlsx模板已生成!保存在%s\n' % self.paths)
        except PermissionError:
            logger.error('iplist init failed', exc_info=True)
            self.gui_obj.set_res('iplist文档已打开,请关闭后重试!\n', 1)
        return 1

    def read_file(self):
        servers = []
        excelfile = xlrd.open_workbook(self.paths)
        sheet = excelfile.sheet_by_index(0)
        if sheet.nrows <= 2 and '127.0.0.1' in sheet.cell_value(1, 0):
            self.gui_obj.set_res('iplist.xlsx为空,请填写服务器信息!\n', 1)
            sys.exit(0)
        if sheet.ncols <= 5:
            self.gui_obj.set_res('iplist.xlsx缺少内容,请重新生成模板并根据提示根据示例填写服务器信息!\n', 1)
            sys.exit(0)
        self.rows = sheet.nrows - 1
        for i in range(1, sheet.nrows):
            if sheet.cell_value(i, 0) == '例：127.0.0.1':
                self.rows -= 1
                continue
            for j in range(6):
                if not sheet.cell_value(i, j):
                    self.gui_obj.set_res('iplist中检查到空数据,第%s行,第%s列,请修改!\n' % (i + 1, 2, sheet.cell_value(i, 1)), 1)
                    sys.exit(0)
            server = {}
            server['ip'] = sheet.cell_value(i, 0).strip()
            a = sheet.cell_value(i, 1)
            try:
                server['port'] = int(a)
            except ValueError:
                self.gui_obj.set_res('iplist中检查到非法数据,第%s行,第%s列,请修改!\n' % (i + 1, 2, sheet.cell_value(i, 1)), 1)
                sys.exit(0)
            server['uname'] = sheet.cell_value(i, 2).strip()
            b = sheet.cell_value(i, 3)
            if isinstance(b, int) or isinstance(b, float):
                server['passwd'] = str(int(b)).strip()
            else:
                server['passwd'] = b.strip()
            israc = sheet.cell_value(i, 4)
            try:
                israc = str(israc)
                server['israc'] = 1 if israc.lower() == 'y' else 0
            except:
                server['israc'] = 1 if israc == '是' else 0
            middle_ware_type = sheet.cell_value(i, 5)
            if middle_ware_type.startswith('T') or middle_ware_type.startswith('t'):
                server['middle_ware_type'] = 'tuxedo'
            elif middle_ware_type.startswith('W') or middle_ware_type.startswith('w'):
                server['middle_ware_type'] = 'weblogic'
            else:
                server['middle_ware_type'] = None
            servers.append(server)
        logger.info('read iplist,servers info:%s' % servers)
        logger.info('servers nums:%s' % self.rows)
        logger.debug('read iplist finish')
        return servers
