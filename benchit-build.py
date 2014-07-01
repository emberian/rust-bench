#!/usr/bin/python3

import base64
import json
import sys
import os

import requests
from plumbum import FG, local
from plumbum.cmd import make, git, cp, mkdir

local.env["PATH"] = "/usr/lib/ccache/bin:" + local.env["PATH"]
git["checkout", sys.argv[1]] & FG

mkdir["-v", "-p", "/var/rust/%s" % sys.argv[1]] & FG
local["../configure"]["--prefix=/var/rust/%s" % sys.argv[1]] & FG
try:
    make["-j8"] & FG
except:
    try:
    # handle transient incorrect make failure (otherwise is a noop and harmless)
        make["-j8"] & FG
    except:
        # only clean if we really have to
        make["clean"] & FG
        make["-j8"] & FG
        make["-j8"] & FG

make["install"] & FG

with open("/var/rust/history.txt", "a") as hist:
    hist.write(git["rev-parse", sys.argv[1]]())
