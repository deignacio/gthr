from mock import Mock, patch
from subprocess import PIPE, STDOUT
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

    def _test_process_line(self, line, expected):
        self._create_gthr([])
        info = self.gthr.process_line(line)
        self.assertEquals(expected, info)

    def test_process_line_no_match(self):
        self._test_process_line('', {})

    def test_process_line_launching(self):
        self._test_process_line('-----> Launching... done, v100',
                                {'version': '100'})

    def test_process_line_refid(self):
        self._test_process_line(' + e20548a...e2524c4 HEAD^ -> master (forced update)',
                                {'src_ref': 'HEAD^'})

    def _test_process_push(self, lines, expected):
        p = Mock()
        p.stdout.readline.side_effect = lambda: lines.pop() if lines else ""

        self._create_gthr([])
        info = self.gthr.process_push(p)
        self.assertEquals(expected, info)

    def test_process_push_none(self):
        self._test_process_push(['hello world\n',
                                'hi mom\n',
                                'not matching\n'],
                               {})

    def test_process_push_launching(self):
        self._test_process_push(['hello world\n',
                                 '-----> Launching... done, v100\n',
                                'hi mom\n'],
                                {'version': '100'})

    def test_process_push_refid(self):
        self._test_process_push(['hello world\n',
                                 ' + e20548a...e2524c4 HEAD^ -> master (forced update)\n',
                                 'hi mom\n'],
                                {'src_ref': 'HEAD^'})

    def test_process_push_both(self):
        self._test_process_push(['hello world\n',
                                 '-----> Launching... done, v100\n',
                                 ' + e20548a...e2524c4 HEAD^ -> master (forced update)\n',
                                'hi mom\n'],
                                {'version': '100',
                                 'src_ref': 'HEAD^'})

    def _test_validate_push(self, wait_value, info, raises=None):
        p = Mock()
        p.wait.return_value = wait_value

        self._create_gthr([])
        if raises:
            self.assertRaises(raises,
                              self.gthr.validate_push,
                              p,
                              info)
        else:
            self.gthr.validate_push(p, info)

    def test_validate_push_ok(self):
        info = {'version': '1', 'src_ref': 'master'}
        wait_value = 0

        self._test_validate_push(wait_value, info)

    def test_validate_push_fail(self):
        info = {'version': '1', 'src_ref': 'master'}
        wait_value = 1

        self._test_validate_push(wait_value, info, SystemExit)

    def test_validate_push_missing_version(self):
        info = {'src_ref': 'master'}
        wait_value = 0

        self._test_validate_push(wait_value, info, SystemExit)

    def test_validate_push_missing_src_ref(self):
        info = {'version': '1'}
        wait_value = 0

        self._test_validate_push(wait_value, info, SystemExit)

    @patch('gthr.Popen')
    def _test_git_tag(self, info, expected_cmd, mock_popen):
        self._create_gthr([])
        p = self.gthr.git_tag(info)
        self.assertTrue(mock_popen.called)
        self.assertEquals(1, mock_popen.call_count)
        call_params = mock_popen.call_args
        args = call_params[0][0]
        kwargs = call_params[1]
        self.assertEquals(expected_cmd, args)
        self.assertEquals({'stdout':PIPE, 'stderr':STDOUT}, kwargs)

    def test_git_tag_success(self):
        info = {'version': '1', 'src_ref': 'master'}
        cmd = ['git', 'tag', '-m', 'gthr tag for heroku release v1', 'heroku-release-v1', 'master']
        self._test_git_tag(info, cmd)
