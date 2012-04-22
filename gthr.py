#!/usr/bin/env python
import re
from subprocess import Popen, PIPE, STDOUT
import sys


class Gthr(object):
    GIT_PUSH = ['git', 'push']
    GIT_TAG = ['git', 'tag']
    TAG_MSG_PATTERN = 'gthr tag for heroku release v%(version)s'
    TAG_PATTERN = 'heroku-release-v%(version)s'

    LAUNCHING_RE = re.compile("^-----> Launching... done, v(?P<version>\d+)$")
    REFID_RE = re.compile("(?P<src_ref>\S+) -> master")

    QUIET_ARGS = ['-q', '--quiet']

    def __init__(self, git_args):
        self.args = git_args[:]

        self.be_quiet = False
        for q_arg in Gthr.QUIET_ARGS:
            if q_arg in self.args:
                self.args.remove(q_arg)
                self.be_quiet = True

    def git_push(self):
        cmd = Gthr.GIT_PUSH + self.args
        return Popen(cmd, stdout=PIPE, stderr=STDOUT)

    def process_line(self, line):
        if not self.be_quiet:
            print line
        m = Gthr.LAUNCHING_RE.match(line)
        if m:
            return m.groupdict()
        m = Gthr.REFID_RE.search(line)
        if m:
            return m.groupdict()
        return {}

    def process_push(self, p):
        info = {}
        for l in iter(p.stdout.readline, ""):
            info.update(**self.process_line(l[:-1]))
        return info


    def validate_push(self, p, info):
        if p.wait():
            msg = 'not tagging:  looks like git push failed'
            raise SystemExit(msg)
        if 'version' not in info:
            msg = 'not tagging:  could not find release number in push output'
            raise SystemExit(msg)
        if 'src_ref' not in info:
            msg = 'not tagging:  could not find a source reference in push output'
            raise SystemExit(msg)

    def git_tag(self, info):
        msg = Gthr.TAG_MSG_PATTERN % info
        tag_name = Gthr.TAG_PATTERN % info
        commit = info['src_ref']
        cmd = Gthr.GIT_TAG + ['-m', msg, tag_name, commit]
        if not self.be_quiet:
            print
            print 'gthr auto tagging repo'
            print '\t', cmd
        return Popen(cmd, stdout=PIPE, stderr=STDOUT)

    def process_tag(self, p):
        if not self.be_quiet:
            for l in iter(p.stdout.readline, ""):
                print l[:-1]

    def validate_tag(self, p):
        if p.wait():
            raise SystemExit('not tagged:  looks like git tag failed')
        if not self.be_quiet:
            print 'gthr auto tagging successful!'


def main():
    args = sys.argv[1:]
    gthr = Gthr(args)

    p = gthr.git_push()
    #  want to build info before waiting so that the
    #  output is printed to stdout as it happens
    info = gthr.process_push(p)
    gthr.validate_push(p, info)

    p = gthr.git_tag(info)
    gthr.process_push(p)
    gthr.validate_tag(p)


if __name__ == '__main__':
    main()
