class Operation(object):
    def __init__(self):
        self.args = ['cpio']

    def will_begin(self):
        raise NotImplementedError

    def do(self):
        raise NotImplementedError

    def will_finish(self):
        raise NotImplementedError