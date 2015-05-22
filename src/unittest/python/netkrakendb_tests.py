from __future__ import print_function

import unittest
from mock import patch, MagicMock, mock_open, call

import netkraken
from netkraken.db import Fetcher, Aggregator
import counterdb


class NetKrakenTests(unittest.TestCase):

    def setUp(self):
        netkraken.settings = {"stagedir": "///invalid///",
                              "finaldir": "///invalid///"}
        self.current_timestrings = {'day': '2042-12-12',
                                    'minute': '2042-12-12T12:12',
                                    'hour': '2042-12-12T12'}

    @patch("subprocess.Popen")
    @patch("netkraken.db.get_current_timestrings")
    def test_fetch(self, current_timestrings, popen):
        current_timestrings.return_value = self.current_timestrings
        popen.return_value = MagicMock()
        popen.return_value.communicate = MagicMock(name="communicate")
        popen.return_value.communicate.return_value = ("""State      Recv-Q Send-Q                   Local Address:Port                       Peer Address:Port
LISTEN     0      80                           localhost:mysql                                 *:*
LISTEN     0      128                          localhost:4243                                  *:*
LISTEN     0      128                                  *:ssh                                   *:*
LISTEN     0      128                                  *:rpc.status                               *:*
ESTAB      0      0                            localhost:46221                         localhost:55982
CLOSE-WAIT 1      0                            localhost:42715                         localhost:38422
ESTAB      0      0                            localhost:55982                         localhost:46221
CLOSE-WAIT 38     0                                  foo:49159                               bar:https
CLOSE-WAIT 58     0                                  foo:49154                               bar:https
""", None)
        counterdb.makedirs = MagicMock(name="makedirs")

        f = Fetcher()
        m = mock_open()
        with patch("counterdb.CountDB._open_file", m, create=True):
            f.fetch()

        m.assert_has_calls([call().write('"foo bar https"')])
        # self.assertEquals("dump me the call stack NOW!", m.mock_calls)

    @patch("glob.glob")
    def test_aggregate(self, globglob):
        netkraken.db.print = netkraken.db.makedirs = counterdb.makedirs = MagicMock()
        globglob.return_value = ("2042-12-12T12:12", "2042-12-12T12:13")

        m = mock_open(read_data='{"counter": 13, "data": {"foo bar braz": 39, "ham egg mont": 13}}')
        with patch("counterdb.CountDB._open_file", m, create=True):
            a = Aggregator()

            a.finalize = MagicMock()
            a.aggregate()

            a.finalize.assert_has_calls([call("2042-12-12T12:12"), call("2042-12-12T12:13")])


if __name__ == "__main__":
    unittest.main()
