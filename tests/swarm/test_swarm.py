#!/usr/bin/env python

"""Tests of wrapper code in pycits.swarm"""

import os
import shutil
import unittest

import pytest

from lpbio import swarm, LPBioNotExecutableError


class TestSwarm(unittest.TestCase):

    """Class collecting tests for Swarm wrapper."""

    def setUp(self):
        """Set up test fixtures"""
        # Input/output paths
        self.testdir = os.path.join("tests", "swarm")
        self.indir = os.path.join(self.testdir, "input")
        self.infile = os.path.join(self.indir, "swarm_coded_with_abundance.fasta")
        self.outdir = os.path.join(self.testdir, "outputs")
        self.outfile = os.path.join(self.outdir, "swarm.out")

        # Target paths
        self.targetdir = os.path.join(self.testdir, "targets")
        self.targetfile = os.path.join(self.targetdir, "swarm.out")

        # remove and recreate the output directory
        try:
            shutil.rmtree(self.outdir)
        except FileNotFoundError:
            pass
        os.makedirs(self.outdir, exist_ok=True)

    @staticmethod
    def test_swarm_wrapper_creation():
        """swarm executable is in $PATH"""
        swarm.Swarm("swarm")

    def test_swarm_parameters(self):
        parameters = swarm.SwarmParameters(t=1, d=1)
        self.assertEqual(parameters.t, 1)
        self.assertEqual(parameters.d, 1)

    def test_swarm_cmd(self):
        """swarm module returns correct form of cmd-line"""
        parameters = swarm.SwarmParameters(t=1, d=1)
        cmd = swarm.build_cmd(self.infile, self.outfile, parameters)
        self.assertEqual(
            cmd, ["swarm", "-t 1", "-d 1", "-o", self.outfile, self.infile]
        )

    def test_swarm_wrapper_cmd(self):
        """swarm wrapper returns correct form of cmd-line"""
        cluster = swarm.Swarm("swarm")
        target = ["swarm", "-t 1", "-d 1", "-o", self.outfile, self.infile]
        parameters = swarm.SwarmParameters(t=1, d=1)
        self.assertEqual(
            cluster.run(self.infile, self.outdir, parameters, dry_run=True), target
        )

    @staticmethod
    def test_swarm_wrapper_exec_notexist():
        """error thrown when swarm executable does not exist"""
        with pytest.raises(LPBioNotExecutableError):
            swarm.Swarm(os.path.join(".", "swarm"))

    def test_swarm_wrapper_run(self):
        """swarm clusters test data"""
        cluster = swarm.Swarm("swarm")

        parameters = swarm.SwarmParameters(t=1, d=1)
        cluster.run(self.infile, self.outdir, parameters)

    def test_swarm_output_parse(self):
        """Swarm runs and output parses correctly"""
        cluster = swarm.Swarm("swarm")

        parameters = swarm.SwarmParameters(t=1, d=1)
        result = cluster.run(self.infile, self.outdir, parameters)

        parser = swarm.SwarmParser()
        target = parser.read(self.targetfile)
        swarms = parser.read(result.outfilename)
        self.assertEqual(target, swarms)
