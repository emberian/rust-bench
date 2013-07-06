#!/usr/bin/python

import base64
import json
import sys
import os

import requests
from plumbum import FG, local
from plumbum.cmd import make, git, cp, mkdir

#local.env["PATH"] = "/usr/lib/ccache/bin:" + local.env["PATH"]
#git["checkout", sys.argv[1]] & FG
#local["../configure"] & FG
#make["clean"] & FG
#make["-j4"] & FG
## handle transient incorrect make failure (otherwise is a noop and harmless)
#make["-j4"] & FG

# forgive me father, for I have sinned
if os.path.exists("../src/librustc/rustc.rc"):
    os.system("mem-bench.py x86_64-unknown-linux-gnu/stage2/bin/rustc -Z time-passes --cfg stage2 -O --target=x86_64-unknown-linux-gnu -o x86_64-unknown-linux-gnu/stage2/lib/rustc/x86_64-unknown-linux-gnu/lib/librustc.so ../src/librustc/rustc.rc > mem.json")
    os.system("/usr/bin/time x86_64-unknown-linux-gnu/stage2/bin/rustc -Z time-passes --cfg stage2 -O --target=x86_64-unknown-linux-gnu -o x86_64-unknown-linux-gnu/stage2/lib/rustc/x86_64-unknown-linux-gnu/lib/librustc.so ../src/librustc/rustc.rc 2>&1 | tail -n2 > time.txt")
else:
    os.system("mem-bench.py x86_64-unknown-linux-gnu/stage2/bin/rustc -Z time-passes --cfg stage2 -O --target=x86_64-unknown-linux-gnu -o x86_64-unknown-linux-gnu/stage2/lib/rustc/x86_64-unknown-linux-gnu/lib/librustc.so ../src/librustc/rustc.rs > mem.json")
    os.system("/usr/bin/time x86_64-unknown-linux-gnu/stage2/bin/rustc -Z time-passes --cfg stage2 -O --target=x86_64-unknown-linux-gnu -o x86_64-unknown-linux-gnu/stage2/lib/rustc/x86_64-unknown-linux-gnu/lib/librustc.so ../src/librustc/rustc.rs 2>&1 | tail -n2 > time.txt")

datadir = "/home/cmr/benches/%s/" % git["rev-parse", sys.argv[1]]().strip()
mkdir["-v", "-p", datadir] & FG
cp["-v", "-t", datadir, "mem.json"] & FG
cp["-v", "-t", datadir, "time.txt"] & FG

with open("/home/cmr/benches/history.txt", "a") as hist:
    hist.write(git["rev-parse", sys.argv[1]]())

with open(datadir + "commit_info.txt", "w") as ci:
    ci.write(git["show", "-s", "--format=%an %aE%n%at%n%s"]())
