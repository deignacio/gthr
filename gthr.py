#!/usr/bin/env python
import re
from subprocess import Popen, PIPE, STDOUT
import sys

GIT_PUSH = ['git', 'push']
GIT_TAG = ['git', 'tag']
TAG_MSG_PATTERN = 'gthr tag for heroku release v%(version)s'
TAG_PATTERN = 'heroku-release-v%(version)s'

LAUNCHING_RE = re.compile("^-----> Launching... done, v(?P<version>\d+)$")
REFID_RE = re.compile("(?P<src_ref>\S+) -> master")

QUIET_ARGS = ['-q', '--quiet']
be_quiet = False


def sanity_check_args(args):
    for q_arg in QUIET_ARGS:
        if q_arg in args:
            args.remove(q_arg)
            be_quiet = True


def git_push(args):
    return Popen(GIT_PUSH + args, stdout=PIPE, stderr=STDOUT)


def process_line(line):
    if not be_quiet:
        print line
    m = LAUNCHING_RE.match(line)
    if m:
        return m.groupdict()
    m = REFID_RE.search(line)
    if m:
        return m.groupdict()
    return {}


def process_push(p):
    info = {}
    for l in iter(p.stdout.readline, ""):
        info.update(**process_line(l[:-1]))
    return info


def validate_push(p, info):
    if p.wait():
        msg = 'not tagging:  looks like git push failed'
        raise SystemExit(msg)
    if 'version' not in info:
        msg = 'not tagging:  could not find release number in push output'
        raise SystemExit(msg)
    if 'src_ref' not in info:
        msg = 'not tagging:  could not find a source reference in push output'
        raise SystemExit(msg)


def git_tag(info):
    msg = TAG_MSG_PATTERN % info
    tag_name = TAG_PATTERN % info
    commit = info['src_ref']
    cmd = GIT_TAG + ['-m', msg, tag_name, commit]
    if not be_quiet:
        print
        print 'gthr auto tagging repo'
        print '\t', cmd
    return Popen(cmd, stdout=PIPE, stderr=STDOUT)


def process_tag(p):
    if not be_quiet:
        for l in iter(p.stdout.readline, ""):
            print l[:-1]


def validate_tag(p):
    if p.wait():
        raise SystemExit('not tagged:  looks like git tag failed')
    if not be_quiet:
        print 'gthr auto tagging successful!'


def main():
    args = sys.argv[1:]
    sanity_check_args(args)

    p = git_push(args)
    #  want to build info before waiting so that the
    #  output is printed to stdout as it happens
    info = process_push(p)
    validate_push(p, info)

    p = git_tag(info)
    process_push(p)
    validate_tag(p)


if __name__ == '__main__':
    main()
