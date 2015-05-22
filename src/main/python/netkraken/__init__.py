from datetime import datetime, timedelta
import os


settings = {
    "stagedir": "/tmp/netconns/__stage__",
    "finaldir": "/tmp/netconns/final"}

formats = {
    "day": "%Y-%m-%d",
    "hour": "%Y-%m-%dT%H",
    "minute": "%Y-%m-%dT%H:%M"}

thresholds = {
    "day": timedelta(days=14),
    "hour": timedelta(hours=4*24),
    "minute": timedelta(minutes=60)}


def get_current_datetime():
    return datetime.now()


def get_current_timestrings():
    now = get_current_datetime()
    tmp = {}
    for key, format in formats.items():
        tmp[key] = now.strftime(format)
    return tmp


def get_stage_filename(timestamp):
    return os.path.join(settings["stagedir"], timestamp)


def get_final_filename(filename_or_timestamp):
    if os.sep in filename_or_timestamp:
        return filename_or_timestamp.replace(settings["stagedir"], settings["finaldir"])
    return os.path.join(settings["finaldir"], filename_or_timestamp)


def get_current_stage_filename():
    return get_stage_filename(get_current_timestrings()["minute"])


def get_timestamp(filename_or_timestamp):
    if os.sep in filename_or_timestamp:
        timestamp_string = os.path.basename(filename_or_timestamp)
    else:
        timestamp_string = filename_or_timestamp
    for level, format in formats.items():
        try:
            datetime.strptime(timestamp_string, format)
            return (level, timestamp_string)
        except:
            pass
    raise Exception("cannot determine timestamp of %s" % timestamp_string)


def get_higher_timestamp(filename_or_timestamp):
    if os.sep in filename_or_timestamp:
        timestamp_string = os.path.basename(filename_or_timestamp)
    else:
        timestamp_string = filename_or_timestamp
    last_level = None
    for level in sorted(formats):  # here: order is day -> hour -> minute, perfect :o)
        format = formats[level]
        try:
            timestamp = datetime.strptime(timestamp_string, format)
            return (last_level, timestamp.strftime(formats[last_level]))
        except:
            last_level = level
    return (None, None)
    # raise Exception("cannot determine higher timestamp of %s" % timestamp_string)
