import unittest

from gthr import Gthr

class GthrTest(unittest.TestCase):
    def setUp(self):
        self.gthr = None

    def _create_gthr(self, git_args):
        self.gthr = Gthr(git_args)

    def _test_be_quiet(self, git_args, expected):
        self._create_gthr(git_args)
        self.assertEquals(expected, self.gthr.be_quiet)
        
    def test_be_quiet_default(self):
        args = ["origin", "master"]
        self._test_be_quiet(args, False)

    def test_be_quiet_q(self):
        args = ["-q", "origin", "master"]
        self._test_be_quiet(args, True)

    def test_be_quiet_quiet(self):
        args = ["--quiet", "origin", "master"]
        self._test_be_quiet(args, True)

