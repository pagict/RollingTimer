from Operation import Operation
import os, os.path
import subprocess


class RestoreOperation(Operation):
    def __init__(self, src, destination):
        super(RestoreOperation, self).__init__()
        self.src = src
        if destination[-1] == '/':
            self.destination = destination[:-1]
        else:
            self.destination = destination
        self.cmd = 'cpio -iv'.split(' ')

    def will_begin(self):
        pass

    def _do_internal(self):
        parent = os.path.split(self.destination)[0]
        os.chdir(parent)
        with open(self.src, 'rb') as tar_file:
            subprocess.Popen(self.cmd, stdin=tar_file, stdout=subprocess.PIPE)

    def will_finish(self):
        pass
