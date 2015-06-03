import shutil
import Operation
import os
import subprocess
import utils


class RestoreOperation(Operation.Operation):
    def __init__(self):
        super(RestoreOperation, self).__init__()

        self.tag = None
        self.destination_name = None
        self.tt = None

        self.src_dict = None
        self.destination_dict = {}
        self.old_working_path = os.getcwd()
        self.op = None

    def set_from_version(self, from_version):
        self.destination_name = from_version.destination
        self.tt = from_version.tt
        self.tag = from_version.tag

    def set_from_device_dict(self, from_device_dict):
        self.src_dict = from_device_dict

    @staticmethod
    def devices():
        device_list = super(RestoreOperation, RestoreOperation).devices()
        return [p for p in device_list if p['LABEL'] == Operation.Operation.BACKUP_PARTITION_LABEL]

    def will_begin(self):
        # get the destination device_dict by its name
        for device in Operation.Operation.devices():
            if device['NAME'] == self.destination_name:
                self.destination_dict = device
                break
        # mount destination
        # utils.mount_device(self.destination_dict)
        # mount src device
        utils.mount_device(self.src_dict)
        self.from_path = os.path.join(self.src_dict['MOUNTPOINT'],
                                      self.tt + Operation.Operation.EXTENSION)
        # self.to_path = self.destination_dict['MOUNTPOINT']

        """
        Delete all destination files before restore.
        This is an ugly implementation for not containing the added files
        after that backup.
        """
        utils.mount_device(self.destination_dict)
        for root, dirs, files in os.walk(self.destination_dict['MOUNTPOINT']):
            for f in files:
                os.remove(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d), True)
        utils.umount_device(self.destination_dict)
        # os.chdir(self.to_path)
    #
    # def _do_internal(self):
    #     # spawn a backend process for not blocking the GUI
    #     self.op = Process(target=self._process_function)
    #     self.op.start()
    #     self.op.join()

    def _do_internal(self):
        cmd = 'fsarchiver restfs {} id=0,dest={} -v'.format(self.from_path,
                                                             self.destination_dict['NAME']).split()
        subprocess.call(cmd)

    def will_finish(self):
        os.chdir(self.old_working_path)
        # utils.umount_device(self.destination_dict)
        utils.umount_device(self.src_dict)
        self.op = None