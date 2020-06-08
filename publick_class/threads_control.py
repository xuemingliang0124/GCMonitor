from threading import Thread


class MyThread(Thread):
    def __init__(self, func, args, name=''):
        Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args

    def run(self):
        self.obj = self.func(*self.args)

    def get_local_result_info(self):
        return {'local_result_path': self.obj.local_result_path, 'result_name': self.obj.resutl_name[0]}

    def get_tag(self):
        try:
            return self.obj.tag
        except:
            return 0
