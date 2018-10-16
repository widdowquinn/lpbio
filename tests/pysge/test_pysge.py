# -*- coding: utf-8 -*-
"""Tests of SGE job submission"""

import shutil
import time
import unittest

import pytest

import pysge


class TestPysge(unittest.TestCase):

    """Class collecting tests for pysge"""

    def test_create_job(self):
        """Create Job for SGE-like scheduler"""
        pysge.Job(name="test_job", command="echo {}".format(time.asctime()))

    def test_create_job_dependencies(self):
        """Create Job with dependencies for SGE-like scheduler"""
        job = pysge.Job(
            name="test_job_dependencies", command="echo {}".format(time.asctime())
        )
        depjobs = [
            pysge.Job(
                name="dependency {}".format(i), command="echo {}".format(time.asctime())
            )
            for i in range(3)
        ]
        [job.add_dependency(depjob) for depjob in depjobs]

    def test_create_jobgroup(self):
        """Create parameter-sweep JobGroup for SGE-like scheduler"""
        args = {"arg1": ["a", "b", "c"]}
        pysge.JobGroup(name="test_jobgroup", command="echo", arguments=args)

    def test_create_jobgroup_dependencies(self):
        """Create parameter-sweep JobGroup with dependencies for SGE-like scheduler"""
        args = {"arg1": ["a", "b", "c"]}
        jobgroup = pysge.JobGroup(
            name="test_jobgroup_dependencies", command="echo", arguments=args
        )
        depjobs = [
            pysge.Job(
                name="dependency {}".format(i), command="echo {}".format(time.asctime())
            )
            for i in range(3)
        ]
        for depjob in depjobs:
            jobgroup.add_dependency(depjob)

    @pytest.mark.skipif(
        shutil.which(pysge.QSUB_DEFAULT) is None,
        reason="qsub executable ({}) could not be found".format(pysge.QSUB_DEFAULT),
    )
    def test_create_run_job(self):
        """Create and run Job with SGE-like scheduler"""
        job = pysge.Job(
            name="test_run_job",
            command="echo {} \\(test_create_run_job\\)".format(time.asctime()),
        )
        pysge.build_and_submit_jobs(job)

    @pytest.mark.skipif(
        shutil.which(pysge.QSUB_DEFAULT) is None,
        reason="qsub executable ({}) could not be found".format(pysge.QSUB_DEFAULT),
    )
    def test_create_run_job_badname(self):
        """Create and run a Job using SGE-like scheduler

        This job has undesirable characters in the name
        """
        job = pysge.Job(
            name="test run job #|!;,.?",
            command="echo This was a bad name! \\(test_create_run_job_badname\\)",
        )
        pysge.build_and_submit_jobs(job)

    @pytest.mark.skipif(
        shutil.which(pysge.QSUB_DEFAULT) is None,
        reason="qsub executable ({}) could not be found".format(pysge.QSUB_DEFAULT),
    )
    def test_create_run_jobgroup(self):
        """Create and run JobGroup with SGE-like scheduler"""
        args = {"arg1": ["a", "b", "c"]}
        jobgroup = pysge.JobGroup(
            name="test_run_jobgroup",
            command="echo $arg1 \\(test_create_run_jobgroup\\)",
            arguments=args,
        )
        pysge.build_and_submit_jobs(jobgroup)

    @pytest.mark.skipif(
        shutil.which(pysge.QSUB_DEFAULT) is None,
        reason="qsub executable ({}) could not be found".format(pysge.QSUB_DEFAULT),
    )
    def test_create_run_job_dependencies(self):
        """Create and run Job with dependencies for SGE-like scheduler"""
        job = pysge.Job(
            name="test_run_job_dependencies",
            command="echo {} \\(test_create_run_job_dependencies\\)".format(
                time.asctime()
            ),
        )
        depjobs = [
            pysge.Job(
                name="testjob_dependency_{}".format(i),
                command="echo {}".format(time.asctime()),
            )
            for i in range(3)
        ]
        for depjob in depjobs:
            job.add_dependency(depjob)
        pysge.build_and_submit_jobs([job] + depjobs)

    @pytest.mark.skipif(
        shutil.which(pysge.QSUB_DEFAULT) is None,
        reason="qsub executable ({}) could not be found".format(pysge.QSUB_DEFAULT),
    )
    def test_create_run_jobgroup_dependencies(self):
        """Create parameter-sweep JobGroup with dependencies for SGE-like scheduler"""
        args = {"arg1": ["a", "b", "c"]}
        jobgroup = pysge.JobGroup(
            name="test_run_jobgroup_dependencies",
            command="echo $arg1 \\(test_create_run_jobgroup_dependencies\\)",
            arguments=args,
        )
        depjobs = [
            pysge.Job(
                name="testjobgroup_dependency_{}".format(i),
                command="echo {}".format(time.asctime()),
            )
            for i in range(3)
        ]
        for depjob in depjobs:
            jobgroup.add_dependency(depjob)
        pysge.build_and_submit_jobs([jobgroup] + depjobs)
