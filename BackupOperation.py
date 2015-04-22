from Operation import Operation
import subprocess, os.path
import utils


class BackupOperation(Operation):
    def __init__(self, src, destination, tag=None):
        super(BackupOperation, self).__init__()
        self.tag = tag
        self.src = os.path.expanduser(src)
        self.destination = os.path.expanduser(destination)
        self.pipe1_cmd = 'find {}/'.format(self.src).split(' ')
        self.pipe2_cmd = 'cpio -ov'.split(' ')

    def will_begin(self):
        pass

    def _do_internal(self):
        name = utils.new_name()
        destination_file = os.path.join(self.destination, name + Operation.EXTENSION)
        op1 = subprocess.Popen(self.pipe1_cmd, stdout=subprocess.PIPE)
        op2 = subprocess.Popen(self.pipe2_cmd, stdin=op1.stdout, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        op1.stdout.close()
        tar_data = op2.communicate()

        tar_file = open(destination_file, 'wb')
        tar_file.write(tar_data[0])

        if self.tag:
            tag = self.tag
        else:
            tag = name
        with open(os.path.join(self.destination, Operation.MAPPING_FILE), 'w+') as map_file:
            map_file.writelines(utils.record_line(tag, name, self.src))

    def will_finish(self):
        pass


if __name__ == '__main__':
    op = BackupOperation('~/rpmbuild', '~/tst_cpio')
    op.do()