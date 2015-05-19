import time
import subprocess
import os
import uuid
import collections
Map = collections.namedtuple('Map', ['tt', 'destination', 'tag'])

DEFAULT_BACKUP_DIR_NAME = 'Backups'

"""
The mapping file is for time-stamp:destination:tag mapping.
Each line in file should be treated as a tuple whose structure is
`time-stamp-string  destination-string  tag-string`. Elements are
separated by space. In case that tag may has space within, the split
method should set a maximum split count.
"""


def all_mappings(mapping_file):
    """
    Read the mapping file, return a list of named tuple
    :param mapping_file: a mapping file stream
    :return: a list
    """
    map_list = [Map(tt=tt, destination=dest, tag=tg) for tt, dest, tg in
                (line.strip().split(None, 2) for line in
                    mapping_file.readlines())]
    return map_list


def record_line(time_stamp, destination, tag):
    """
    Return the (time_stamp, destination, tag) string, for appending the mapping file
    @:type tag: str
    @:type time_stamp: str
    @:type destination: str
    :rtype str: a formatted string like 'tag time_stamp'
    """
    return '{} {} {}\n'.format(time_stamp, destination, tag)


def new_name():
    """
    Return a formatted string represents the current time
    :rtype str: current time string
    """
    t = time.localtime(time.time())
    return '{:04d}-{:02d}-{:02d}_{:02d}{:02d}{:02d}'.format(t.tm_year, t.tm_mon, t.tm_mday,
                                                            t.tm_hour, t.tm_min, t.tm_sec)

"""
    Indicates what values in what keys is NOT available for that device.
    Which should be removed from the available devices list.
"""
exclusive_map = {'NAME': ['sr0', 'sda2'],
                 'TYPE': ['disk', 'rom', 'loop', 'dm'], }
"""
    Defines what columns would get from the `lsblk` command
"""
device_info_column = ['NAME', 'TYPE', 'MODEL', 'SERIAL', 'SIZE', 'MOUNTPOINT']


def special_care_for_sda3(device_list):
    for device in device_list:
        if device['NAME'] == 'sda3':
            device['MOUNTPOINT'] = os.path.join(device['MOUNTPOINT'],
                                                DEFAULT_BACKUP_DIR_NAME)


def filter_devices_dec(fun):
    """
    filter the devices list
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
        special_care_for_sda3(devices)
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
        line += ' '
        d = {k: v[1:].strip() for k, v in (p.split('=') for p in line.split('" ') if len(p))}
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


def mount_device(device_dict):
    if device_dict['MOUNTPOINT'] == '':
        device_dict['MOUNTPOINT'] = '/tmp/{}'.format(uuid.uuid1())
        os.mkdir(device_dict['MOUNTPOINT'])
        dev_path = '/dev/'+device_dict['NAME']
        subprocess.call('mount {} {}'.format(dev_path, device_dict['MOUNTPOINT']).split())
    elif device_dict['NAME'] == 'sda3':
        # Again, special care for sda3 which mounted on /run/initramfs/isoscan
        subprocess.call('mount -o remount,rw {}'.format('/run/initramfs/isoscan').split())


def umount_device(device_dict):
    last_component = os.path.split(device_dict['MOUNTPOINT'])[1]
    try:                        # The last component is a uuid string
        uuid.UUID(last_component)
        subprocess.call('umount {}'.format(device_dict['MOUNTPOINT']).split())
        os.rmdir(device_dict['MOUNTPOINT'])
        device_dict['MOUNTPOINT'] = ''
    except ValueError:          # It mounted automatically
        # special care for sda3
        if device_dict['NAME'] == 'sda3':
            subprocess.call('mount -o remount,ro {}'.format('/run/initramfs/isoscan').split())


def size_of_path(path):
    """
    Get the size in byte of the given path.
    If the path point to a file, then return the file size.
    If the path point to a directory, return a directory size recursively.
    (Without following symbolic links).
    :param path:
    :return: Size in byte
    """
    cmd = 'du -sb {}'.format(path).split()
    try:
        size, name = subprocess.check_output(cmd).split()
        return size
    except subprocess.CalledProcessError:
        pass