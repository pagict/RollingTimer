import time
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


def record(tag, time_stamp):
    """
    append the (tag time_stamp) pair to the mapping file
    :param tag:
    :param time_stamp:
    :return:
    """
    with open(MAPPING_FILE_NAME, 'a') as mapping_file:
        s = '{} {}\n'.format(tag, time_stamp)
        mapping_file.writelines(s)


def new_name():
    t = time.localtime(time.time())
    return '{}-{}-{}_{}:{}:{}'.format(t.tm_year, t.tm_mon, t.tm_mday,
                                      t.tm_hour, t.tm_min, t.tm_sec)