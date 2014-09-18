#!/usr/bin/python3

import base64
import json
import sys
import os

import requests
from plumbum import FG, local
from plumbum.cmd import make, git, cp, mkdir, find

os.environ["PATH"] = "/usr/lib/ccache/bin:" + local.env["PATH"]
os.environ["CFG_VERSION"] = "bench"
os.environ["CFG_LIBDIR"] = "/"
os.environ["CFG_LIBDIR_RELATIVE"] = "/"
os.environ["CFG_RUSTLIBDIR"] = "/"
os.environ["LIBDIR_RELATIVE"] = "whatisthisIdon'teven"
os.environ["CFG_COMPILER_TRIPLE"] = "---"
os.environ["CFG_COMPILER"] = "foobar"
os.environ["CFG_PREFIX"] = "/"
os.environ["CFG_COMPILER_HOST_TRIPLE"] = "yay"
os.environ["CFG_RELEASE"] = "ffff"

git["checkout", "-f", sys.argv[1]] & FG

if os.path.exists("/mnt/rustb/%s" % sys.argv[1]):
    a = sys.argv[1]
    os.system("make librustc/lib/llvmdeps.rs")

    args = "--emit bc -L x86_64-unknown-linux-gnu/llvm/Release+Asserts/lib -Z time-passes --cfg stage2 -O --target=x86_64-unknown-linux-gnu -o /tmp/rustc.so"

    # forgive me father, for I have sinned
    try:
        if os.path.exists("../src/librustc/rustc.rc"):
            print("Memory Benching now")
            assert 0 == os.system("mem-bench /mnt/rustb/%s/stage2/bin/rustc %s ../src/librustc/rustc.rc > mem.json" % (a, args))
            print("Time benching now")
            assert 0 == os.system("/usr/bin/time /mnt/rustb/%s/stage2/bin/rustc %s ../src/librustc/rustc.rc 2>&1 | tail -n2 > time.txt" % (a, args))
        else:
            print("Memory Benching now")
            assert 0 == os.system("mem-bench /mnt/rustb/%s/stage2/bin/rustc %s ../src/librustc/lib.rs > mem.json" % (a, args))
            print("Time benching now")
            assert 0 == os.system("/usr/bin/time /mnt/rustb/%s/stage2/bin/rustc %s ../src/librustc/lib.rs 2>&1 | tail -n2 > time.txt" % (a, args))
    except AssertionError:
        args = "--emit-llvm -L x86_64-unknown-linux-gnu/llvm/Release+Asserts/lib -Z time-passes --cfg stage2 -O --target=x86_64-unknown-linux-gnu -o /tmp/rustc.so"
        if os.path.exists("../src/librustc/rustc.rc"):
            print("Memory Benching now")
            assert 0 == os.system("mem-bench /mnt/rustb/%s/stage2/bin/rustc %s ../src/librustc/rustc.rc > mem.json" % (a, args))
            print("Time benching now")
            assert 0 == os.system("/usr/bin/time /mnt/rustb/%s/stage2/bin/rustc %s ../src/librustc/rustc.rc 2>&1 | tail -n2 > time.txt" % (a, args))
        else:
            print("Memory Benching now")
            assert 0 == os.system("mem-bench /mnt/rustb/%s/stage2/bin/rustc %s ../src/librustc/lib.rs > mem.json" % (a, args))
            print("Time benching now")
            assert 0 == os.system("/usr/bin/time /mnt/rustb/%s/stage2/bin/rustc %s ../src/librustc/lib.rs 2>&1 | tail -n2 > time.txt" % (a, args))

    datadir = "/home/cmr/benches/data/%s/" % git["rev-parse", sys.argv[1]]().strip()
    mkdir["-v", "-p", datadir] & FG
    cp["-v", "-t", datadir, "mem.json"] & FG
    cp["-v", "-t", datadir, "time.txt"] & FG
    find("/mnt/rustb/%s" % a, "-type", "f", "-printf", "%p %s\n") > (os.path.join(datadir, "sizes.txt"))

    with open(datadir + "commit_info.txt", "w") as ci:
        ci.write(git["show", "-s", "--format=%an %aE%n%at%n%s"]())
else:
    with open("/home/cmr/benches/todo.txt", "a") as f:
        f.write(sys.argv[1] + '\n')

with open("/home/cmr/benches/history.txt", "a") as f:
    f.write(sys.argv[1] + '\n')
