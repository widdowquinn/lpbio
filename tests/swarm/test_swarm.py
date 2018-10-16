#!/usr/bin/env python

"""Tests of wrapper code in pycits.swarm"""

import os
import shutil
import unittest

import pytest

from lpbio import swarm, LPBioNotExecutableError

# Input/output paths
TESTDIR = os.path.join("tests", "swarm")
INDIR = os.path.join(TESTDIR, "input")
INFILE = os.path.join(INDIR, "swarm_coded_with_abundance.fasta")
OUTDIR = os.path.join(TESTDIR, "outputs")
os.makedirs(OUTDIR, exist_ok=True)
OUTFILE = os.path.join(OUTDIR, "swarm.out")

# Target paths
TARGETDIR = os.path.join(TESTDIR, "targets")
TARGETFILE = os.path.join(TARGETDIR, "swarm.out")


class TestSwarm(unittest.TestCase):

    """Class collecting tests for Swarm wrapper."""

    def setUp(self):
        """Set up test fixtures"""
        try:
            shutil.rmtree(OUTDIR)
        except FileNotFoundError:
            pass
        os.makedirs(OUTDIR, exist_ok=True)

    def test_swarm_wrapper_creation(self):
        """swarm executable is in $PATH"""
        swarm.Swarm("swarm")

    def test_swarm_parameters(self):
        parameters = swarm.SwarmParameters(t=1, d=1)
        self.assertEqual(parameters.t, 1)
        self.assertEqual(parameters.d, 1)

    def test_swarm_cmd(self):
        """swarm module returns correct form of cmd-line"""
        parameters = swarm.SwarmParameters(t=1, d=1)
        cmd = swarm.build_cmd(INFILE, OUTFILE, parameters)
        self.assertEqual(cmd, ["swarm", "-t 1", "-d 1", "-o", OUTFILE, INFILE])

    def test_swarm_wrapper_cmd(self):
        """swarm wrapper returns correct form of cmd-line"""
        cluster = swarm.Swarm("swarm")
        target = ["swarm", "-t 1", "-d 1", "-o", OUTFILE, INFILE]
        parameters = swarm.SwarmParameters(t=1, d=1)
        self.assertEqual(cluster.run(INFILE, OUTDIR, parameters, dry_run=True), target)

    def test_swarm_wrapper_exec_notexist(self):
        """error thrown when swarm executable does not exist"""
        with pytest.raises(LPBioNotExecutableError):
            swarm.Swarm(os.path.join(".", "swarm"))

    def test_swarm_wrapper_run(self):
        """swarm clusters test data"""
        cluster = swarm.Swarm("swarm")

        parameters = swarm.SwarmParameters(t=1, d=1)
        cluster.run(INFILE, OUTDIR, parameters)

    def test_swarm_output_parse(self):
        """Swarm runs and output parses correctly"""
        cluster = swarm.Swarm("swarm")

        parameters = swarm.SwarmParameters(t=1, d=1)
        result = cluster.run(INFILE, OUTDIR, parameters)

        parser = swarm.SwarmParser()
        target = parser.read(TARGETFILE)
        swarms = parser.read(result.outfilename)
        self.assertEqual(target, swarms)
