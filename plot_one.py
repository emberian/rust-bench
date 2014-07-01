#!/usr/bin/env python2
from __future__ import division

import argparse
import json

import matplotlib as mpl
mpl.use("Agg")

import matplotlib.pyplot as p
from plumbum.cmd import git

parser = argparse.ArgumentParser()
parser.add_argument("first", help="json (from mem-bench.py) from the run")
parser.add_argument("-t", "--title", help="title of graph")

args = parser.parse_args()

x1, y1 = zip(*json.loads(open(args.first).read())["memory_data"])
y1 = map(lambda x: x / (1024 ** 2), y1)
p.suptitle(args.title or "Compiling librustc with stage2 compiler")
p.xlabel("Time (seconds)")
p.ylabel("Memory (mebibytes)")

p.plot(x1, y1, lw=0.7, c="#1111dd")

p.grid()
p.legend(loc="lower center", fontsize="small")
p.gca().set_axis_bgcolor("#e5e5e5")
p.savefig("rustc.png", facecolor="#f5f5f5")
