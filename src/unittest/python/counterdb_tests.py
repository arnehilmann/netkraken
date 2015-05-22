from __future__ import print_function

import unittest
from mock import patch

from counterdb import CountDB


class CountDBTests(unittest.TestCase):

    def setUp(self):
        self.dummy_countdb = CountDB("///invalid/filename///")
        self.dummy_countdb.data = {"foo": 42}
        self.dummy_countdb.counter = 2

    def test_opening_nonexisting_file_raises_exception(self):
        self.assertRaises(IOError, CountDB.open, "///invalid///")

    @patch("counterdb.CountDB.open")
    def test_dump(self, countdb_mock):
        countdb_mock.return_value = self.dummy_countdb
        cdb = CountDB.open("///dummy///")
        result = cdb.convert_to_relative()
        self.assertDictEqual({"foo": 21.0}, result)

        import StringIO
        output = StringIO.StringIO()
        cdb.dump(stream=output)
        self.assertEquals("foo 21.000\n", output.getvalue())

    def test_counting(self):
        cdb = CountDB.open_for_counting("///unused///")
        cdb.count("bar")
        self.assertDictEqual({"bar": 1.0}, cdb.convert_to_relative())
        self.assertRaises(Exception, cdb.extend, CountDB("///unusedtoo///"))

    def test_extending(self):
        cdb = CountDB.open_for_extending("///unused///")
        self.assertRaises(Exception, cdb.count, "bar")
        cdb.extend(self.dummy_countdb)
        self.assertDictEqual({"foo": 21.0}, cdb.convert_to_relative())


if __name__ == "__main__":
    unittest.main()
