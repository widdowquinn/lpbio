# -*- coding: utf-8 -*-
"""Code for interaction with the Swarm clustering tool."""

import os
import shlex
import shutil
import subprocess

from collections import namedtuple

from lpbio import LPBioNotExecutableError, is_exe


class SwarmError(Exception):
    """Exception raised when swarm fails"""

    def __init__(self, msg):
        self.message = msg


# factory class for Swarm run returned values
SwarmRun = namedtuple("SwarmRun", "command outfilename stdout stderr")

# factory class for Swarm parameter values
SwarmParameters = namedtuple("SwarmParameters", "t d")
SwarmParameters.__new__.__defaults__ = (1, 1)


def build_cmd(infname, outfname, parameters):
    """Build a command-line for swarm"""
    params = [
        "-{0} {1}".format(shlex.quote(str(k)), shlex.quote(str(v)))
        for k, v in parameters._asdict().items()
        if v is not None
    ]
    cmd = ["swarm", *params, "-o", shlex.quote(outfname), shlex.quote(infname)]
    return cmd


class Swarm(object):
    """Class for working with SWARM"""

    def __init__(self, exe_path):
        """Instantiate with location of executable"""
        exe_path = shlex.quote(shutil.which(exe_path))
        if not os.access(exe_path, os.X_OK):
            msg = "{0} is not an executable".format(exe_path)
            raise LPBioNotExecutableError(msg)
        self._exe_path = exe_path

    def run(self, infname, outdir, parameters, dry_run=False):
        """Run swarm to cluster sequences in the passed file

        - infname    - path to sequences for clustering
        - outdir     - output directory for clustered output
        - parameters - named tuple of Swarm parameters
        - dry_run    - if True returns cmd-line but does not run

        Returns namedtuple with form:
          "command outfilename stdout stderr"
        """
        self.__build_cmd(infname, outdir, parameters)
        if dry_run:
            return self._cmd
        pipe = subprocess.run(
            self._cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            shell=False,
        )
        results = SwarmRun(self._cmd, self._outfname, pipe.stdout, pipe.stderr)
        return results

    def __build_cmd(self, infname, outdir, parameters):
        """Build a command-line for swarm"""
        self._outfname = os.path.join(shlex.quote(outdir), "swarm.out")
        self._cmd = build_cmd(infname, self._outfname, parameters)


class SwarmCluster(object):
    """Describes a single Swarm cluster"""

    def __init__(self, amplicons, parent=None):
        self._amplicons = tuple(sorted(amplicons))
        if parent:
            self._parent = parent

    def __len__(self):
        """Returns the number of amplicons in the cluster"""
        return len(self._amplicons)

    def __getitem__(self, item):
        """Return sequence IDs from the swarm like a list"""
        return self._amplicons[item]

    @property
    def amplicons(self):
        """The amplicons in a swarm cluster"""
        return self._amplicons

    @property
    def abundance(self):
        """Returns the total abundance of all amplicons in the cluster"""
        return sum(self.abundances)

    @property
    def abundances(self):
        """Returns a list of abundance of each amplicons in the cluster"""
        return [int(amp.split("_")[-1]) for amp in self._amplicons]


class SwarmResult(object):
    """Describes the contents of a Swarm output file"""

    def __init__(self, name):
        self._name = name
        self._clusters = list()

    def add_swarm(self, amplicons):
        """Adds a list of amplicon IDs as a SwarmCluster"""
        self._clusters.append(SwarmCluster(amplicons, self))

    def __eq__(self, other):
        """Returns True if all swarms match all swarms in passed result"""
        # this test relies on the amplicons being ordered tuples
        these_amplicons = {c.amplicons for c in self._clusters}
        other_amplicons = {c.amplicons for c in other._clusters}
        return these_amplicons == other_amplicons

    def __len__(self):
        """Returns the number of swarms in the result"""
        return len(self._clusters)

    def __str__(self):
        """Return human-readable representation of the SwarmResult"""
        outstr = "\n".join(
            ["SwarmResult: {}".format(self.name), "\tSwarms: {}".format(len(self))]
        )
        swarmstr = []
        for idx, swarm in enumerate(self._clusters):
            swarmstr.append("\t\tSwarm {}, size: {}".format(idx, len(swarm)))
        swarmstr = "\n".join(swarmstr)
        return "\n".join([outstr + swarmstr])

    def __getitem__(self, item):
        """Return swarm clusters like a list"""
        return self._clusters[item]

    @property
    def swarms(self):
        """The clusters produced by a swarm run"""
        return self._clusters[:]

    @property
    def name(self):
        """The swarm result filename"""
        return self._name


class SwarmParser(object):
    """Parser for Swarm cluster output"""

    @classmethod
    def read(SwarmParser, fname):
        """Parses the passed Swarm output file into a SwarmResult"""
        result = SwarmResult(fname)
        with open(fname, "r") as swarms:
            for swarm in swarms:
                result.add_swarm(swarm.strip().split())
        return result

    def __init__(self):
        pass
