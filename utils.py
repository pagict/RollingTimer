import time
import subprocess
MAPPING_FILE_NAME = 'mappings'


class TagNotFound(Exception):
    """
    When a tag didn't exist in the mappings file, raise a TagNotFound exception
    """
    pass


def time_stamp_from_tag(tag):
    """
    Read the (tag time_stamp) mapping file, find the time_stamp string
    correspondent to the tag. If no this tag, raise a TagNotFound exception
    :param tag:
    :return:
    """
    with open(MAPPING_FILE_NAME, 'r') as mapping_file:
        map = dict(tuple(line.split(None,-1) for line in mapping_file))
        tt = map.get(tag)
        if tt:
            return tt

        raise TagNotFound


def record_line(tag, time_stamp):
    """
    Return the (tag time_stamp) pair, for appending the mapping file
    @:type tag: str
    @:type time_stamp: str
    :rtype str: a formatted string like 'tag time_stamp'
    """
    return '{} {}\n'.format(tag, time_stamp)


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
    cmd = 'lsblk -Pn -o NAME,TYPE,LABEL,MODEL,SERIAL,SIZE'
    output = subprocess.check_output(cmd.split(' '))
    for line in output.splitlines():
        d = {k: v[1:].strip() for k, v in (p.split('=') for p in line.split('" '))}
        devices.append(d)
    return devices