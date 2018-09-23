# -*- coding: utf-8 -*-
"""Provides the Swarm object, wrapping a call to the tool"""

import subprocess

from lpbio import NotExecutableError, is_exe
from lpbio.swarm import build_cmd, SwarmRun


class Swarm(object):
    """Class for working with SWARM"""

    def __init__(self, exe_path):
        """Instantiate with location of executable"""
        if not is_exe(exe_path):
            msg = "{0} is not an executable".format(exe_path)
            raise NotExecutableError(msg)
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
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        results = SwarmRun(self._cmd, self._outfname, pipe.stdout, pipe.stderr)
        return results

    def __build_cmd(self, infname, outdir, parameters):
        """Build a command-line for swarm"""
        self._cmd = build_cmd(infname, outdir, parameters)

