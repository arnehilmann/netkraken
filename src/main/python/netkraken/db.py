#!/usr/bin/env python
from __future__ import print_function

from datetime import datetime
import glob
import os
import shutil
import subprocess

from netkraken import (settings,
                       formats,
                       thresholds,
                       get_current_timestrings,
                       get_timestamp,
                       get_higher_timestamp,
                       get_stage_filename,
                       get_final_filename)
from counterdb import CountDB, makedirs


class Fetcher(object):
    def __init__(self):
        self.timestamp = get_current_timestrings()["minute"]
        self.filename = get_stage_filename(self.timestamp)

    def fetch(self):
        with CountDB.open_for_counting(self.filename) as db:
            ssp = subprocess.Popen(["ss", "-t4ar"], stdout=subprocess.PIPE)
            stdout, _ = ssp.communicate()
            listening = set()
            for line in stdout.splitlines()[2:]:
                state, recv, send, local, foreign = line.split()
                local_host, local_port = local.split(b':')
                if state == "LISTEN":
                    listening.add(local_port)
                    continue
                if local_port in listening:
                    continue  # ignore incoming connections completely
                    # source = foreign
                    # target = local
                else:
                    source = local
                    target = foreign
                source_host, source_port = source.split(b':')
                target_host, target_port = target.split(b':')
                if b'*' in source_host or b'*' in target_host:
                    continue
                if source_host.startswith(b"localhost") and target_host.startswith(b"localhost"):
                    continue
                connection = b" ".join((source_host, target_host, target_port))
                db.count(connection.decode(encoding='UTF-8'))

    def dump(self):
        with CountDB.open(self.filename) as db:
            db.dump()


class Aggregator(object):
    def __init__(self):
        self.current = get_current_timestrings()

    def aggregate(self):
        for filename in sorted(glob.glob(os.path.join(settings["stagedir"], "*")), key=len, reverse=True):
            level, timestamp = get_timestamp(filename)
            print("stage: %s [%s]" % (filename, level))

            if self.is_current(level, timestamp):
                print("\tis current, ignoring for now")
                continue

            if self.is_too_old(level, timestamp):
                print("\ttoo old, ignoring")
                self.remove(filename)
                continue

            higher_level, higher_timestamp = get_higher_timestamp(filename)
            print("\thigher level: %s [%s]" % (higher_timestamp, higher_level))
            if not higher_level:
                continue

            if self.is_finalized(higher_timestamp):
                print("\t%s slot %s already finalized, ignoring" % (higher_level, higher_timestamp))
                self.remove(filename)
                continue

            # from here: filename is not current, not already finalized, not too old
            self.aggregate_file(filename, higher_timestamp)
            self.finalize(filename)

        for filename in sorted(glob.glob(os.path.join(settings["finaldir"], "*"))):
            level, timestamp = get_timestamp(filename)
            print("final: %s [%s]" % (filename, level))
            if self.is_too_old(level, timestamp):
                print("\ttoo old, removing")
                self.remove(filename)

    def finalize(self, filename):
        final_filename = get_final_filename(filename)
        print("\tfinalize %s -> %s" % (filename, final_filename))
        # use finalize() on CountDB
        makedirs(final_filename)
        shutil.move(filename, final_filename)

    def aggregate_file(self, filename, timestamp):
        higher_stage_filename = get_stage_filename(timestamp)
        print("\taggregating in %s" % higher_stage_filename)
        with CountDB.open_for_extending(higher_stage_filename) as aggregated_db:
            with CountDB.open(filename) as db:
                aggregated_db.extend(db)

    def is_too_old(self, level, timestamp):
        current_dt = datetime.strptime(self.current[level], formats[level])
        timestamp_dt = datetime.strptime(timestamp, formats[level])
        delta = current_dt - timestamp_dt
        return delta > thresholds[level]

    def is_current(self, level, timestamp):
        return self.current[level] == timestamp

    def is_finalized(self, timestamp):
        higher_final_filename = get_final_filename(timestamp)
        return os.path.exists(higher_final_filename)

    def remove(self, filename):
        print("\tremoving")
        shutil.move(filename, os.path.join("/tmp", os.path.basename(filename)))
        # os.remove(filename)
