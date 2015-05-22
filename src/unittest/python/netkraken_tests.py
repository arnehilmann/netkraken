from __future__ import print_function

from datetime import datetime

import unittest
from mock import patch

import netkraken


class NetKrakenTests(unittest.TestCase):

    def test_get_timestamp(self):
        self.assertEquals(("minute", "2042-12-12T12:12"),
                          netkraken.get_timestamp("2042-12-12T12:12"))
        self.assertEquals(("minute", "2042-12-12T12:12"),
                          netkraken.get_timestamp("///foo///2042-12-12T12:12"))
        self.assertRaises(Exception, netkraken.get_timestamp, "no-valid-date")

    def test_get_higher_timestamp(self):
        self.assertEquals(("hour", "2042-12-12T12"),
                          netkraken.get_higher_timestamp("///foo///2042-12-12T12:12"))
        self.assertEquals(("day", "2042-12-12"),
                          netkraken.get_higher_timestamp("///foo///2042-12-12T12"))

    @patch("netkraken.get_current_datetime")
    def test_get_current_timestrings(self, now_mock):
        now_mock.return_value = datetime(2042, 12, 12, 12, 12)
        self.assertDictEqual({'day': '2042-12-12', 'hour': '2042-12-12T12', 'minute': '2042-12-12T12:12'}, 
                             netkraken.get_current_timestrings())


if __name__ == "__main__":
    unittest.main()
