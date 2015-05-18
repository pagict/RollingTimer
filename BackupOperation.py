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
        self.op = None

    def will_begin(self):
        utils.mount_device(self.src)
        utils.mount_device(self.destination)
        self.from_path = self.src['MOUNTPOINT']
        os.chdir(self.from_path)
        name = utils.new_name()
        self.to_path = os.path.join(self.destination['MOUNTPOINT'],
                                    name + Operation.EXTENSION)

    # def _do_internal(self):
    #     # spawn a backend process for not blocking the GUI
    #     self.op = Process(target=self._process_function)
    #     self.op.start()
    #     # Won't step next until the process finishing its job
    #     self.op.join()

    def _do_internal(self):
        """
        A backend process separate from GUI to do the real backup operation.
        :return:
        """
        pipe1_cmd = 'find'.split()
        op1 = subprocess.Popen(pipe1_cmd, stdout=subprocess.PIPE)
        pipe2_cmd = 'cpio -ov --file={}'.format(self.to_path).split()
        subprocess.call(pipe2_cmd,
                        stdin=op1.stdout,
                        bufsize=OUTPUT_BUFFER_SIZE)

    def will_finish(self):
        # Retrieve the time-stamp as the default tag
        name = os.path.basename(self.to_path)[:-len(Operation.EXTENSION)]
        if self.tag:
            tag = self.tag
        else:
            tag = name
        # write mapping file
        with open(os.path.join(self.destination['MOUNTPOINT'],
                               Operation.MAPPING_FILE),
                  'a') as map_file:
            map_file.writelines(utils.record_line(name, self.src['NAME'], tag))

        os.chdir(self.old_path)
        utils.umount_device(self.src)
        utils.umount_device(self.destination)

        self.op = None
