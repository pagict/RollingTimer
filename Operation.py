import utils
import os


class Operation(object):
    EXTENSION = '.tar'
    MAPPING_FILE = 'mapping'

    def __init__(self):
        self.args = None
        self.op = None
        self.from_path = None
        self.to_path = None

    def will_begin(self):
        raise NotImplementedError

    def _do_internal(self):
        raise NotImplementedError

    def do(self):
        self.will_begin()
        self._do_internal()
        self.will_finish()

    def will_finish(self):
        raise NotImplementedError

    @property
    def progress_percentage(self):
        """
        :return: Return the progress percentage between range(0, 100)
        If it's a backup operation, from_path is the backup tar file,
            to_path is the recovery destination directory.
        If it's a restore operation, from_path is the directory need to
            backup, to_path is the backup tar file.
        """
        if self.op is None:
            return 0

        # For some mysterious reasons, this conditional statement isn't
        # work properly. But if just remove it, the restore operation
        # will never finish. Let's first comment it, and figure a way out.
        # ToDO: The restore operation will never end. How to detect a
        # ToDO:     Operation is finished?
        # if not self.op.is_alive():
        #   return 100

        total_size = utils.size_of_path(self.from_path)
        current_size = utils.size_of_path(self.to_path)
        percentage = float(current_size) / float(total_size)
        # The percentage might be larger than 1.0 for a reason,
        # which would be the inefficiency of the tar compression algorithm,
        # or additional information like checksum consumed the disk usage.
        # So if the percentage goes larger than 1.0, we could assume that
        # the the operation is done.
        if percentage > 1.0000:
            percentage = 1.0000
        return int(percentage*100)

    devices_cache = []

    @staticmethod
    def devices():
        """
        Return a list of all filtered devices. Each is a dictionary.
        It first check the cache, only run `lsblk` when cache is empty.
        :return: A list of all filtered devices. Each is a dictionary.
        """
        if not Operation.devices_cache:
            Operation.devices_cache = utils.available_devices()
        return Operation.devices_cache

    @staticmethod
    def versions_from_device(device_dict):
        """
        To look up a version list from a device.
        A version item is a mapping tuple defined in utils.py.
        Please refer to the utils.py for detailed structure.
        If it had cached, return directly from the cache, or mount the device,
        read the mapping file, get the version list stored in cache, and umount
        the device.
        :param device_dict: The device you want to look up.
        :return: A list of versions. Each is string.
        """
        devices = Operation.devices()
        # find the cached device
        d = {}
        for d in devices:
            if d['NAME'] == device_dict['NAME']:
                break
        # check whether the tags are cached
        tags = d.get('TAGS', None)
        if tags:
            return tags
        # no tags cache, mount the device, get the tags to the cache, umount
        utils.mount_device(d)
        with open(os.path.join(d['MOUNTPOINT'], Operation.MAPPING_FILE), 'r') as map_file:
            d['TAGS'] = utils.all_mappings(map_file)
        utils.umount_device(d)
        return d['TAGS']