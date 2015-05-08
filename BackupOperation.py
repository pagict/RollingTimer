from multiprocessing import Process
from Operation import Operation
import subprocess
import os
import utils
import copy

OUTPUT_BUFFER_SIZE = 512


class BackupOperation(Operation):
    def __init__(self, src, destination, tag=None):
        super(BackupOperation, self).__init__()
        self.tag = tag
        self.src = copy.deepcopy(src)
        self.destination = copy.deepcopy(destination)
        self.old_path = os.getcwd()
        self.destination_file = ''
        self.op = None

    def will_begin(self):
        utils.mount_device(self.src)
        utils.mount_device(self.destination)
        os.chdir(self.src['MOUNTPOINT'])
        name = utils.new_name()
        self.destination_file = os.path.join(self.destination['MOUNTPOINT'],
                                             name + Operation.EXTENSION)

    def _do_internal(self):
        self.op = Process(target=self._process_function)
        self.op.start()
        # Won't step next until the process finishing its job
        self.op.join()

    def _process_function(self):
        """
        A backend process separate from GUI to do the real backup operation.
        :return:
        """
        pipe1_cmd = 'find'.split()
        op1 = subprocess.Popen(pipe1_cmd, stdout=subprocess.PIPE)
        pipe2_cmd = 'cpio -ov --file={}'.format(self.destination_file).split()
        subprocess.Popen(pipe2_cmd,
                         stdin=op1.stdout,
                         bufsize=OUTPUT_BUFFER_SIZE)

    def will_finish(self):
        # Retrieve the time-stamp as the default tag
        name = os.path.basename(self.destination_file)[:-len(Operation.EXTENSION)]
        if self.tag:
            tag = self.tag
        else:
            tag = name
        # write mapping file
        with open(os.path.join(self.destination['MOUNTPOINT'],
                               Operation.MAPPING_FILE),
                  'a') as map_file:
            map_file.writelines(utils.record_line(name, self.src['NAME'], tag))

        utils.umount_device(self.src)
        utils.umount_device(self.destination)

        os.chdir(self.old_path)
        self.op = None

    @property
    def progress_percentage(self):
        """
        :return: Return the progress percentage between range(0, 100)
        """
        if self.op is None:
            return 0
        if not self.op.is_alive():
            return 100

        total_size = utils.size_of_path(self.src['MOUNTPOINT'])
        current_size = utils.size_of_path(self.destination_file)
        percentage = float(current_size) / float(total_size)
        # The percentage might be larger than 1.0 for a reason,
        # which would be the inefficiency of the tar compression algorithm,
        # or additional information like checksum consumed the disk usage.
        # So if the percentage goes larger than 1.0, we could assume that
        # the the operation is done.
        if percentage > 1.0000:
            percentage = 1.0000
        return int(percentage*100)
