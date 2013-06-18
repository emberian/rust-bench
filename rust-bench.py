#!/usr/bin/env python3
import os
import sys
import json
import logging

from plumbum import local
from plumbum.cmd import rustc, sleep, sudo, cgcreate

from benchlib import measure_cmd, process_stat


def avg(l):
    return sum(l) / len(l)

if len(sys.argv) != 2:
    sys.stderr.write("incorrect arguments: %s /path/to/cratename.rs\n" % sys.argv[0])
    sys.exit()
else:
    crate = sys.argv[1]

user = os.environ['USER']
filename = os.getenv('RBENCH_LOGFILE', 'rustbench.log')
binname = os.path.splitext(os.path.split(crate)[-1])[0] + '.' + str(os.getpid())
try:
    os.remove(filename)
except:
    pass

logging.basicConfig(level=logging.DEBUG, filename=filename)

# get rustc sha

sha = rustc["--version"]().split(" (")[1].split(" ")[0]

logging.debug("rust sha: %r" % sha)

# do overhead adjustment (assume that 1 second is enough to accurately gague
# overhead, and that sleep 1 actually sleeps for 1 second)
overhead = avg([x.elapsed - 1 for x in (measure_cmd(sleep['1']),
                measure_cmd(sleep['1']), measure_cmd(sleep['1']))])

logging.debug("overhead: %r" % overhead)

if "#[bench]" in open(crate).read():
    benchrunner = True
else:
    benchrunner = False

if benchrunner:
    rustcc = rustc["--test"]
else:
    rustcc = rustc

rustcc = rustcc["-Z", "time-passes", "-O", "-o", binname, crate]
rustc_output = measure_cmd(rustcc)

data = {}

data["crate"] = crate
data["rustc"] = rcd = dict(rustc_output.__dict__)
rcd["sha"] = sha
rcd["cli"] = str(rustcc)
rcd["elapsed"] = rcd["elapsed"] - overhead
rcd["memory_data"] = process_stat(rcd["memory_data"])
rcd["cpuacct"] = dict(rcd["cpuacct"].__dict__)
rcd["pass_timing"] = pt = []

# extract pass timing
for line in rustc_output.stdout.split("\n")[:-1]:
    cols = line.split(" ")
    name = line.split("\t")[-1]
    pt.append((name, float(cols[1])))

prcd = local["./" + str(binname)]

if benchrunner:
    prcd = prcd["--bench"]

program_output = measure_cmd(prcd)

data["program"] = pr = dict(program_output.__dict__)
pr["elapsed"] = pr["elapsed"] - overhead
pr["cli"] = str(prcd)
pr["memory_data"] = process_stat(pr["memory_data"])
pr["cpuacct"] = dict(pr["cpuacct"].__dict__)

sys.stdout.write(json.dumps(data) + "\n")
