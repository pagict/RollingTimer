import time
import subprocess
import os.path
MAPPING_FILE_NAME = 'mappings'


class TagNotFound(Exception):
    """
    When a tag didn't exist in the mappings file, raise a TagNotFound exception
    """
    pass


def time_stamp_destination_from_tag(mapping_file, tag):
    """
    Read the (tag time_stamp destination) mapping file, find the
    (time_stamp string destination_path) tuple correspondent to
     the tag. If no this tag, raise a TagNotFound exception.
    :param tag:
    :return:
    """
    tt_dest_map = {k: (tt, dest) for k, tt, dest in
                   (line.strip().split(None, 2) for line in
                    mapping_file.readlines())}
    tt_dest = tt_dest_map.get(tag)
    if tt_dest:
        return tt_dest

    raise TagNotFound


def record_line(tag, time_stamp, destination):
    """
    Return the (tag, time_stamp, destination) pair, for appending the mapping file
    @:type tag: str
    @:type time_stamp: str
    @:type destination: str
    :rtype str: a formatted string like 'tag time_stamp'
    """
    return '{} {} {}\n'.format(tag, time_stamp, destination)


def new_name():
    """
    Return a formatted string represents the current time
    :rtype str: current time string
    """
    t = time.localtime(time.time())
    return '{:04d}-{:02d}-{:02d}_{:02d}:{:02d}:{:02d}'.format(t.tm_year, t.tm_mon, t.tm_mday,
                                                              t.tm_hour, t.tm_min, t.tm_sec)

"""
    Indicates what values in what keys is NOT available for that device.
    Which should be removed from the available devices list.
"""
exclusive_map = {'TYPE': ['lvm', 'loop', 'rom', 'dm']}

"""
    Defines what columns would get from the `lsblk` command
"""
device_info_column = ['NAME', 'TYPE', 'MODEL', 'SERIAL', 'SIZE']


def filter_devices_dec(fun):
    """
    filter the devices list
    :param fun:
    :return:
    """
    def _dec():
        devices = fun()
        for filter_key in exclusive_map.keys():
            to_be_removed = []
            for item in devices:
                if item[filter_key] in exclusive_map[filter_key]:
                    # Since the remove method taken effect immediately,
                    # which would distort the list during iteration,
                    # we'd better record it first, remove it after
                    # this iteration.
                    to_be_removed.append(item)
            # Here we remove exclusive items. Using list comprehension for compact
            devices = [item for index, item in enumerate(devices) if item not in to_be_removed]
        return devices
    return _dec


@filter_devices_dec
def available_devices():
    """
    Get all block devices.
    :return:A list of dictionaries. Each dictionary is a block device.
    """
    devices = []
    cmd = 'lsblk -Pn'
    if len(device_info_column) > 0:
        cmd = cmd + ' -o ' + ','.join(device_info_column)
    output = subprocess.check_output(cmd.split(' '))
    for line in output.splitlines():
        d = {k: v[1:].strip() for k, v in (p.split('=') for p in line.split('" '))}
        devices.append(d)
    return devices


def parent_path(path):
    """
    Get the parent path of the given path
    :param path:
    :return: parent path
    """
    if path[-1] == '/':
        path = path[:-1]
    return os.path.split(path)[0]
