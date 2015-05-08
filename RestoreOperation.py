import Operation
import os
import subprocess
import utils


class RestoreOperation(Operation.Operation):
    def __init__(self, from_device_dict, from_version):
        super(RestoreOperation, self).__init__()

        self.tag = from_version.tag
        self.destination_name = from_version.destination
        self.tt = from_version.tt

        self.src_dict = from_device_dict
        self.destination_dict = {}
        self.old_path = os.getcwd()
        self.op = None

    def will_begin(self):
        # get the destination device_dict by its name
        for device in Operation.Operation.devices():
            if device['NAME'] == self.destination_name:
                self.destination_dict = device
                break
        # mount destination
        utils.mount_device(self.destination_dict)
        # mount src device
        utils.mount_device(self.src_dict)
        os.chdir(self.destination_dict['MOUNTPOINT'])

    def _do_internal(self):
        src_file_name = os.path.join(self.src_dict['MOUNTPOINT'],
                                     self.tt + Operation.Operation.EXTENSION)
        cmd = 'cpio -iv --file={}'.format(src_file_name).split()
        self.op = subprocess.Popen(cmd)
        self.op.wait()

    def will_finish(self):
        utils.umount_device(self.destination_dict)
        utils.umount_device(self.src_dict)
        os.chdir(self.old_path)