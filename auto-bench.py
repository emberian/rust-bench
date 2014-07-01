#!/usr/bin/python2
import os
from plumbum import local, FG
from plumbum.cmd import git

# the commits already tested
HISTORY = '/home/cmr/benches/data'

BUILDDIR = '/mnt/rustb'

BENCH_OVERRIDE = '/home/cmr/benches/bench-override.txt'


def run(hash):
    local['benchit.py'][hash] & FG

for hash in open(BENCH_OVERRIDE).read().split('\n'):
    if len(hash) == 40:
        local['benchit.py'][hash] & FG

for d in os.listdir(BUILDDIR):
    if not os.path.exists(os.path.join(HISTORY, d)):
        run(d)
