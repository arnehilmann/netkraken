#!/usr/bin/env python
from __future__ import division

from datetime import datetime
import json
import os
import sys

from netkraken import makedirs


class CountDB(object):

    @classmethod
    def open(clazz, filename):
        self = CountDB(filename)
        self.mode = "readonly"  # TODO use enums/constants for self.mode instead of plain strings
        self.load()
        return self

    @classmethod
    def open_for_counting(clazz, filename):
        self = CountDB(filename)
        self.mode = "count"
        try:
            self.load()
        except:
            self.counter = 0
        self.counter += 1
        return self

    @classmethod
    def open_for_extending(clazz, filename):
        self = CountDB(filename)
        self.mode = "extend"
        try:
            self.load()
        except:
            self.counter = 0
        return self

    def __init__(self, filename):
        self.filename = filename
        self.data = {}
        self.counter = 0
        self.mode = "readonly"

    def load(self):
        with open(self.filename) as data_file:
            tmp = json.load(data_file)
            self.data = tmp.get("data", {})
            self.counter = tmp.get("counter", 0)

    def dump(self, format=None, stream=None):
        if not format:
            format = "text"
        if not stream:
            stream = sys.stdout
        getattr(self, "dump_" + format)(stream)

    def dump_text(self, stream):
        for key, count in sorted(self.convert_to_relative().items()):
            stream.write("%s %.3f\n" % (key, count))

    def convert_to_relative(self):
        tmp = self.data.copy()
        for key in tmp:
            tmp[key] = tmp[key] / self.counter
        return tmp

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        if self.mode != "readonly":
            self.persist()

    def count(self, key, increment=1):
        if self.mode != "count":
            raise Exception("countdb not opened for count (consider using open_for_counting)")
        self.data[key] = self.data.get(key, 0) + increment

    def extend(self, other):
        if self.mode != "extend":
            raise Exception("countdb not opened for extend (consider using open_for_extending)")
        self.counter += 1
        for key, count in other.convert_to_relative().items():
            self.data[key] = self.data.get(key, 0) + count

    def persist(self):
        if self.mode == "readonly":
            raise Exception("countdb not opened for modifications (consider using open_for_counting or open_for_extending)")
        makedirs(self.filename)
        with open(self.filename, "w") as data_file:
            json.dump({"data": self.data, "counter": self.counter}, data_file, indent=4)
            data_file.write("\n")

    def finalize(self, final_filename):
        makedirs(final_filename)
        with open(final_filename, "w") as final_file:
            json.dump(self.convert_to_relative(), final_file)
            final_file.write("\n")

