from Operation import Operation
import subprocess
import os
import utils
import copy

OUTPUT_BUFFER_SIZE = 1024


class BackupOperation(Operation):
    def __init__(self, src, destination, tag=None):
        super(BackupOperation, self).__init__()
        self.tag = tag
        self.src = copy.deepcopy(src)
        self.destination = copy.deepcopy(destination)
        self.old_path = os.getcwd()

    def will_begin(self):
        utils.mount_device(self.src)
        utils.mount_device(self.destination)
        os.chdir(self.src['MOUNTPOINT'])

    def _do_internal(self):
        pipe1_cmd = 'find'.split()
        pipe2_cmd = 'cpio -ov'.split()
        name = utils.new_name()
        destination_file = os.path.join(self.destination['MOUNTPOINT'],
                                        name + Operation.EXTENSION)
        op1 = subprocess.Popen(pipe1_cmd, stdout=subprocess.PIPE)
        op2 = subprocess.Popen(
            pipe2_cmd, stdin=op1.stdout,
            stderr=subprocess.PIPE, stdout=subprocess.PIPE,
            bufsize=OUTPUT_BUFFER_SIZE)
        with open(destination_file, 'wb') as tar_file:
            for c in iter(lambda: op2.stdout.read(1), ''):
                tar_file.write(c)
        # tar_file.write(subprocess.check_output(pipe2_cmd, stdin=op1.stdout))

        # op2 = subprocess.Popen(pipe2_cmd, stdin=op1.stdout, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        # op1.stdout.close()
        # tar_data = op2.communicate()
        #
        # tar_file = open(destination_file, 'wb')
        # tar_file.write(tar_data[0])
        # tar_file.close()

        if self.tag:
            tag = self.tag
        else:
            tag = name
        with open(os.path.join(self.destination['MOUNTPOINT'], Operation.MAPPING_FILE), 'a') as map_file:
            map_file.writelines(utils.record_line(name, self.src['NAME'], tag))

    def will_finish(self):
        utils.umount_device(self.src)
        utils.umount_device(self.destination)
        os.chdir(self.old_path)


if __name__ == '__main__':
    op = BackupOperation('~/rpmbuild', '~/tst_cpio')
    op.do()