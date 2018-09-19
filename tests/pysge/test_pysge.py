# -*- coding: utf-8 -*-
"""Tests of SGE job submission"""

import pytest
import shutil
import time

import pysge


def test_create_job():
    """Create Job for SGE-like scheduler"""
    pysge.Job(name="test_job", command="echo {}".format(time.asctime()))


def test_create_job_dependencies():
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


def test_create_jobgroup():
    """Create parameter-sweep JobGroup for SGE-like scheduler"""
    args = {"arg1": ["a", "b", "c"]}
    pysge.JobGroup(name="test_jobgroup", command="echo", arguments=args)


def test_create_jobgroup_dependencies():
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
def test_create_run_job():
    """Create and run Job with SGE-like scheduler"""
    job = pysge.Job(name="test_run_job", command="echo {}".format(time.asctime()))
    pysge.build_and_submit_jobs(job)


@pytest.mark.skipif(
    shutil.which(pysge.QSUB_DEFAULT) is None,
    reason="qsub executable ({}) could not be found".format(pysge.QSUB_DEFAULT),
)
def test_create_run_jobgroup():
    """Create and run JobGroup with SGE-like scheduler"""
    args = {"arg1": ["a", "b", "c"]}
    jobgroup = pysge.JobGroup(
        name="test_run_jobgroup", command="echo $arg1", arguments=args
    )
    pysge.build_and_submit_jobs(jobgroup)


@pytest.mark.skip(reason="make single job calls work, first")
@pytest.mark.skipif(
    shutil.which(pysge.QSUB_DEFAULT) is None,
    reason="qsub executable ({}) could not be found".format(pysge.QSUB_DEFAULT),
)
def test_create_run_job_dependencies():
    """Create and run Job with dependencies for SGE-like scheduler"""
    job = pysge.Job(
        name="test_run_job_dependencies", command="echo {}".format(time.asctime())
    )
    depjobs = [
        pysge.Job(
            name="dependency {}".format(i), command="echo {}".format(time.asctime())
        )
        for i in range(3)
    ]
    for depjob in depjobs:
        job.add_dependency(depjob)
    pysge.build_and_submit_jobs(job)


@pytest.mark.skip(reason="make single job calls work, first")
@pytest.mark.skipif(
    shutil.which(pysge.QSUB_DEFAULT) is None,
    reason="qsub executable ({}) could not be found".format(pysge.QSUB_DEFAULT),
)
def test_create_run_jobgroup_dependencies():
    """Create parameter-sweep JobGroup with dependencies for SGE-like scheduler"""
    args = {"arg1": ["a", "b", "c"]}
    jobgroup = pysge.JobGroup(
        name="test_run_jobgroup_dependencies", command="echo $arg1", arguments=args
    )
    depjobs = [
        pysge.Job(
            name="dependency {}".format(i), command="echo {}".format(time.asctime())
        )
        for i in range(3)
    ]
    for depjob in depjobs:
        jobgroup.add_dependency(depjob)
    pysge.build_and_submit_jobs(jobgroup)
