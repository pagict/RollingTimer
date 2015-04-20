class Operation(object):
    EXTENSION = '.tar'
    MAPPING_FILE = 'mapping'

    def __init__(self):
        self.args = None

    def will_begin(self):
        raise NotImplementedError

    def _do_internal(self):
        raise NotImplementedError

    def do(self):
        self.will_begin()
        self._do_internal()
        self.will_finish()

    def will_finish(self):
        raise NotImplementedError