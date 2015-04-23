from Operation import Operation
import os
import subprocess
import utils


class RestoreOperation(Operation):
    def __init__(self, src_dir, tag):
        super(RestoreOperation, self).__init__()
        with open(os.path.join(src_dir, Operation.MAPPING_FILE), 'r') as mapping_file:
            self.src, self.destination = utils.time_stamp_destination_from_tag(mapping_file, tag)
        self.src = os.path.join(src_dir, self.src) + Operation.EXTENSION
        self.cmd = 'cpio -iv'.split(' ')

    def will_begin(self):
        pass

    def _do_internal(self):
        parent = utils.parent_path(self.destination)
        os.chdir(parent)
        with open(self.src, 'rb') as tar_file:
            subprocess.Popen(self.cmd, stdin=tar_file, stdout=subprocess.PIPE)

    def will_finish(self):
        pass

    @staticmethod
    def all_tags(device_path):
        with open(os.path.join(device_path, Operation.MAPPING_FILE), 'r') as map_file:
            tags = [tag for tag, tt, dest in (line.split() for line in map_file.readlines())]
            return tags

if __name__ == '__main__':
    # op = RestoreOperation('/root/tst_cpio', '2015-04-22_11:10:00')
    print(RestoreOperation.all_tags('/root/tst_cpio'))