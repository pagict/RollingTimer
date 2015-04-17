from Operation import Operation
import subprocess, os.path
import utils


class BackupOperation(Operation):
    def __init__(self, src, destination):
        super(BackupOperation, self).__init__()
        self.src = os.path.expanduser(src)
        self.destination = os.path.expanduser(destination)
        self.destination = '{}/{}.tar'.format(self.destination, utils.new_name())
        self.pipe1 = 'find {}/'.format(self.src).split(' ')
        self.pipe2 = 'cpio -ov'.format(self.destination).split(' ')
        print(self.pipe1)
        print(self.pipe2)
        self.op1 = subprocess.Popen(self.pipe1, stdout=subprocess.PIPE)
        self.op2 = subprocess.Popen(self.pipe2, stdin=self.op1.stdout, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        self.op1.stdout.close()
        r = self.op2.communicate()
        #print(r)
        rfile = open(self.destination, 'wb')
        rfile.write(r[0])


    def will_begin(self):
        pass

    def do(self):
        pass

    def will_finish(self):
        pass


if __name__ == '__main__':
    op = BackupOperation('~/rpmbuild', '~/tst_cpio')