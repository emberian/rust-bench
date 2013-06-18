# A tool for benchmarking rust programs. Knows how to understand the built-in
# benchmark runner too.

# Requires Linux (cgroups), sudo, and the tools from libcgroup.

# Depends on plumbum

from __future__ import division

import os
import sys
import time
import json
import random
import logging
from collections import namedtuple

from plumbum import cli, BG, FG, local
from plumbum.cmd import rustc, sudo, cgcreate, cgexec, cgget, sleep


def _t():
    return time.clock_gettime(time.CLOCK_MONOTONIC)


def _r():
    return str(int(random.random() * 100000))

cmd_stats = namedtuple('cmd_stats', ('elapsed', 'memory_data',
                                                'max_memory', 'cpuacct',
                                                'stdout', 'stderr'))
cpuacct_stats = namedtuple('cpuacct_stats', ('hz', 'user', 'system',
                                             'usage'))


class CGroup(object):
    def __init__(self, controllers=("memory", ), basepath="/sys/fs/cgroup",
                 uid=os.environ["USER"], name=None, prefix=None):
        """
        Create a new cgroup with the given controllers, returning the name
        used. Pass in `name` to customize the name used. The `prefix` argument
        will always be called with the name, allowing the caller to customize
        the name before any potential use of the name.

        Uses sudo.
        """
        if name is None:
            self.name = str(os.getpid())
        else:
            self.name = name

        if prefix is None:
            self.name = "rustbench/" + self.name + '-' + _r()
        else:
            self.name = prefix(self.name)

        self.controllers = controllers
        self.basepath = basepath
        self.uid = uid

    def __enter__(self):
        sudo[cgcreate["-a", self.uid, "-t", self.uid, "-g",
                      ','.join(self.controllers) + ':' + self.name]]()
        return self

    def __exit__(self, type, value, traceback):
        for controller in self.controllers:
            os.rmdir(os.path.join(self.basepath, controller, self.name))

    def var(self, varname, controller="memory"):
        return open(os.path.join(self.basepath, controller, self.name,
                                 varname)).read()

    def mstat(self):
        return self.var("memory.stat")

    def libcg_arg(self):
        return ','.join(self.controllers) + ':' + self.name


def measure_cmd(cmd):
    """
    Run a plumbum command in a cgroup, measuring real time elapsed, and
    cpuacct information
    """
    memory_data = []
    elapsed = None
    max_memory = None
    cpuacct = None
    stdout = None
    stderr = None

    with CGroup(controllers=("memory", "cpuacct")) as cg:
        t1 = _t()
        fut = cgexec["-g", cg.libcg_arg(), cmd] & BG
        while not fut.poll():
            memory_data.append((_t(), cg.mstat()))
        t2 = _t()
        elapsed = t2 - t1
        # adjust timestamps to be relative to start of execution
        memory_data = [(t - t1, d) for t, d in memory_data]
        # collect stats
        max_memory = int(cg.var("memory.max_usage_in_bytes"))
        cau = cg.var("cpuacct.usage", controller="cpuacct")
        cas = cg.var("cpuacct.stat", controller="cpuacct").split("\n")[:-1]
        user_hz = 1 / os.sysconf(os.sysconf_names['SC_CLK_TCK'])
        logging.debug("hz/cas: %r / %r" % (user_hz, cas))
        cpuacct = cpuacct_stats(user_hz, int(cas[0].split(' ')[1]) * user_hz,
                                int(cas[1].split(' ')[1]) * user_hz, int(cau))
        # get output
        stdout = fut.stdout
        stderr = fut.stderr

    return cmd_stats(elapsed, memory_data, max_memory, cpuacct, stdout, stderr)


def process_stat(stat):
    """
    Parse and sort (by time) memory usage information
    """
    output = []
    prev_mem = 0
    for datum in stat:
        d = datum[1]
        memory = 0
        for line in d.split("\n"):
            if line == "":
                break
            k, v = line.split(" ")
            if k in ("total_cache", "total_rss", "total_swap"):
                memory += int(v)
        # collapse adjacent memory usages
        if memory != prev_mem:
            output.append((datum[0], memory))
            prev_mem = memory
    return sorted(output, key=lambda d: d[0])
