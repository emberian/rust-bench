#!/usr/bin/python2
from plumbum import local, FG
from plumbum.cmd import git

# the commits already tested
HISTORY='/var/rust/history.txt'

# put hashes (one per line) into this file to force it to build them
OVERRIDE='/var/rust/build-override.txt'

# the last commit tested by the autostepper
LAST_AUTO='/var/rust/last_auto.txt'

# How many commits to skip over at a time for the auto stepper
TIME_MACHINE_SPEED=1

def run(hash):
    local['benchit-build.py'][hash] & FG

old_hash = git['rev-parse', 'master']().strip()
try:
    print git['pull','mozilla','master'] & FG
except:
    # oh noez, no internet connect? cosmic rays? time machine!
    pass
new_hash = git['rev-parse', 'master']().strip()

if old_hash != new_hash:
    print 'Running from master: %s' % new_hash
    run(new_hash)
    # Rewind the time machine; assumes newer info more valuable than older,
    # and that the auto step will do the Right Thing (TM)
    with open(LAST_AUTO, 'w') as f:
        f.write(new_hash)
else:
    try:
        # read the first line from OVERRIDE, and use it as the commit
        with open(OVERRIDE) as f:
            (hash, rest_of_file) = f.read().split('\n', 1)
        print 'Found override: %s' % hash
        run(hash)

        # write the rest of the file back to OVERRIDE
        with open(OVERRIDE, 'w') as f:
            f.write(rest_of_file)
    except Exception as e:
        # Find a commit to run on automatically

        print 'No override, auto stepping: %s' % e

        # no new master commit, and no overrides, so just run
        # backwards from where we left off last time.
        with open(LAST_AUTO) as f:
            last_auto = f.read().strip()

        already_done = set(open(HISTORY).read().strip().split('\n'))

        next_auto = git['rev-parse', '%s~%d' % (last_auto, TIME_MACHINE_SPEED)]().strip()

        # skip over commits already done.
        while next_auto in already_done:
            print 'skipping: %s' % next_auto
            next_auto = git['rev-parse', '%s~%d' % (next_auto, TIME_MACHINE_SPEED)]().strip()

        print 'Auto stepper: %s' % next_auto
        run(next_auto)

        # record the one we just ran
        with open(LAST_AUTO, 'w') as f:
            f.write(next_auto)
