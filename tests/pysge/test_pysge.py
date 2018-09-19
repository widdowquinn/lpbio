# -*- coding: utf-8 -*-
"""Tests of SGE job submission"""

import pytest
import shutil
import time

import pysge


def test_create_job():
    """Create Job for SGE-like scheduler"""
    job = pysge.Job(name="test job", command="echo {}".format(time.asctime()))


def test_create_job_dependencies():
    """Create Job with dependencies for SGE-like scheduler"""
    job = pysge.Job(name="test job", command="echo {}".format(time.asctime()))
    job.dependencies = [
        pysge.Job(
            name="dependency {}".format(i), command="echo {}".format(time.asctime())
        )
        for i in range(3)
    ]


def test_create_jobgroup():
    """Create parameter-sweep JobGroup for SGE-like scheduler"""
    args = {"arg1": ["a", "b", "c"]}
    jobgroup = pysge.JobGroup(name="test jobgroup", command="echo", arguments=args)


def test_create_jobgroup_dependencies():
    """Create parameter-sweep JobGroup with dependencies for SGE-like scheduler"""
    args = {"arg1": ["a", "b", "c"]}
    jobgroup = pysge.JobGroup(name="test jobgroup", command="echo", arguments=args)
    jobgroup.dependencies = [
        pysge.Job(
            name="dependency {}".format(i), command="echo {}".format(time.asctime())
        )
        for i in range(3)
    ]


@pytest.mark.skipif(
    shutil.which(pysge.QSUB_DEFAULT) is None,
    reason="qsub executable ({}) could not be found".format(pysge.QSUB_DEFAULT),
)
def test_create_run_job():
    """Create and run Job with SGE-like scheduler"""
    job = pysge.Job(name="test job", command="echo {}".format(time.asctime()))
    pysge.build_and_submit_jobs(job)


@pytest.mark.skipif(
    shutil.which(pysge.QSUB_DEFAULT) is None,
    reason="qsub executable ({}) could not be found".format(pysge.QSUB_DEFAULT),
)
def test_create_run_jobgroup():
    """Create and run JobGroup with SGE-like scheduler"""
    args = {"arg1": ["a", "b", "c"]}
    jobgroup = pysge.JobGroup(name="test jobgroup", command="echo", arguments=args)
    pysge.build_and_submit_jobs(jobgroup)


@pytest.mark.skipif(
    shutil.which(pysge.QSUB_DEFAULT) is None,
    reason="qsub executable ({}) could not be found".format(pysge.QSUB_DEFAULT),
)
def test_create_run_job_dependencies():
    """Create and run Job with dependencies for SGE-like scheduler"""
    job = pysge.Job(name="test job", command="echo {}".format(time.asctime()))
    job.dependencies = [
        pysge.Job(
            name="dependency {}".format(i), command="echo {}".format(time.asctime())
        )
        for i in range(3)
    ]
    pysge.build_and_submit_jobs(job)


@pytest.mark.skipif(
    shutil.which(pysge.QSUB_DEFAULT) is None,
    reason="qsub executable ({}) could not be found".format(pysge.QSUB_DEFAULT),
)
def test_create_run_jobgroup_dependencies():
    """Create parameter-sweep JobGroup with dependencies for SGE-like scheduler"""
    args = {"arg1": ["a", "b", "c"]}
    jobgroup = pysge.JobGroup(name="test jobgroup", command="echo", arguments=args)
    jobgroup.dependencies = [
        pysge.Job(
            name="dependency {}".format(i), command="echo {}".format(time.asctime())
        )
        for i in range(3)
    ]
    pysge.build_and_submit_jobs(jobgroup)
