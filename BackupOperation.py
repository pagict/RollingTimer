import Operation
import subprocess
import os
import utils
import copy

OUTPUT_BUFFER_SIZE = 512


class BackupOperation(Operation.Operation):
    def __init__(self):
        super(BackupOperation, self).__init__()
        self.tag = None
        self.src = None
        self.destination = None
        self.old_path = os.getcwd()
        self.op = None

    def set_src(self, src):
        self.src = copy.deepcopy(src)

    def set_destination(self, destination):
        self.destination = copy.deepcopy(destination)

    def set_tag(self, tag=None):
        self.tag = tag

    @staticmethod
    def devices():
        device_list = super(BackupOperation, BackupOperation).devices()
        return [p for p in device_list if p['LABEL'] == Operation.Operation.BACKUP_PARTITION_LABEL]

    def will_begin(self):
        # utils.mount_device(self.src)
        utils.mount_device(self.destination)
        # self.from_path = self.src['MOUNTPOINT']
        # os.chdir(self.from_path)
        name = utils.new_name()
        self.to_path = os.path.join(self.destination['MOUNTPOINT'],
                                    name + Operation.Operation.EXTENSION)

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
        pipe2_cmd = 'fsarchiver savefs {} {} -v'.format(self.to_path, self.src['NAME']).split()
        subprocess.call(pipe2_cmd)

    def will_finish(self):
        # Retrieve the time-stamp as the default tag
        name = os.path.basename(self.to_path)[:-len(Operation.Operation.EXTENSION)]
        if self.tag:
            tag = self.tag
        else:
            tag = name
        # write mapping file
        with open(os.path.join(self.destination['MOUNTPOINT'],
                               Operation.Operation.MAPPING_FILE),
                  'a') as map_file:
            map_file.writelines(utils.record_line(name, self.src['NAME'], tag))

        os.chdir(self.old_path)
        # utils.umount_device(self.src)
        utils.umount_device(self.destination)

        self.op = None
