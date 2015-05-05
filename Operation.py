import utils
import os


class Operation(object):
    EXTENSION = '.tar'
    MAPPING_FILE = 'mapping'

    def __init__(self):
        self.args = None

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