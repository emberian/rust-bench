#!/usr/bin/python3
import os
import sys
import json
import logging

from plumbum import local
from plumbum.commands import BaseCommand as BC
from plumbum.cmd import rustc, sleep, sudo, cgcreate

from benchlib import measure_cmd, process_stat


def avg(l):
    return sum(l) / len(l)

cmd = sys.argv[1:]

user = os.environ['USER']

filename = os.getenv('MEMBENCH_LOGFILE', 'membench.log')
try:
    os.remove(filename)
except:
    pass

logging.basicConfig(level=logging.DEBUG, filename=filename)

cmd = local[cmd[0]][tuple(cmd[1:])]

outp = measure_cmd(cmd, delay=0)

data = dict(outp.__dict__)
data["cli"] = str(cmd)
data["memory_data"] = process_stat(outp.memory_data)
data["cpuacct"] = dict(outp.cpuacct.__dict__)

sys.stdout.write(json.dumps(data) + "\n")
