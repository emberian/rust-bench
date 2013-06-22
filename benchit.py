#!/usr/bin/env python2

import base64
import json
import sys
import os

import github
import requests
from plumbum import FG
from plumbum.cmd import make, git, hub, R

imgur_id = "232aa2b16959bfd"


def post_image(path):
    header = {"Authorization": "Client-ID " + imgur_id}
    img = base64.b64encode(open(path).read())
    parms = {"type": "base64", "image": img}
    r = requests.post("https://api.imgur.com/3/upload", data=img, headers=header)
    j = r.json()
    print(j)

# get baseline measurement
git["checkout", "master"] & FG
make["-j6"] & FG
# forgive me father, for I have sinned
os.system("mem-bench.py x86_64-unknown-linux-gnu/stage2/bin/rustc --cfg stage2 -O -Z no-debug-borrows --target=x86_64-unknown-linux-gnu -o x86_64-unknown-linux-gnu/stage2/lib/rustc/x86_64-unknown-linux-gnu/lib/librustc.so /home/cmr/hacking/rust/src/librustc/rustc.rc > baseline.json")
os.system("time x86_64-unknown-linux-gnu/stage2/bin/rustc --cfg stage2 -O -Z no-debug-borrows --target=x86_64-unknown-linux-gnu -o x86_64-unknown-linux-gnu/stage2/lib/rustc/x86_64-unknown-linux-gnu/lib/librustc.so /home/cmr/hacking/rust/src/librustc/rustc.rc > time_baseline.txt")
git["checkout", sys.argv[1]] & FG
make["-j6"] & FG
os.system("mem-bench.py x86_64-unknown-linux-gnu/stage2/bin/rustc --cfg stage2 -O -Z no-debug-borrows --target=x86_64-unknown-linux-gnu -o x86_64-unknown-linux-gnu/stage2/lib/rustc/x86_64-unknown-linux-gnu/lib/librustc.so /home/cmr/hacking/rust/src/librustc/rustc.rc > data.json")
os.system("time x86_64-unknown-linux-gnu/stage2/bin/rustc --cfg stage2 -O -Z no-debug-borrows --target=x86_64-unknown-linux-gnu -o x86_64-unknown-linux-gnu/stage2/lib/rustc/x86_64-unknown-linux-gnu/lib/librustc.so /home/cmr/hacking/rust/src/librustc/rustc.rc > time_data.txt")
r = (R["--no-save", "--args", "rustc.png", "master (%s)" % git["rev-parse", "master"]().strip()[:7], "%s (%s)" % (sys.argv[1], git["rev-parse", sys.argv[1]]().strip()[:7]), "baseline.json", "data.json"] < "/home/cmr/.local/bin/plot-twoprogs.R")
print(str(r))
r & FG

post_image("rustc.png")
