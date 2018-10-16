# -*- coding: utf-8 -*-
"""Module to support use of SGE-like schedulers

The code is based on the package sge.py detailed below.

-----------------------------------------------------------------------
ORIGINAL COMMENTS
Creative Commons Attribution License
http://creativecommons.org/licenses/by/2.5/

Trevor Strohman
   First release: December 2005
   This version:  11 January 2006

Bug finders: Fernando Diaz

The above-named package had the following documentation on the (now
defunct) page:

http://ciir.cs.umass.edu/~strohman/code/
-----------------------------------------------------------------------

This Python library is meant to allow submission of several jobs, and
large parameter-sweep submissions to a Grid Engine cluster.

Each individual cluster job is represented by a Job object, and these
objects can have dependencies on other jobs.

Parameter sweeps are handled by JobGroup objects, which take the
command, parameter names and parameter values as arguments.

Once a JobGroup, or a set of job objects has been created, the
sge.build_and_submit_jobs function dispatches these jobs for execution
on the cluster.

The module automatically redirects stdout and stderr of the submitted jobs.

sge.py (Requires Python 2.x, Sun Grid Engine 6.0)

This module extends and modifies the original interface, and adds
comments and documentation concerning the
operation of the code.
==============================================================================
"""

import os
import shlex
import shutil
import subprocess

from .Job import Job  # noqa: F401
from .JobGroup import JobGroup

# Default location for qsub executable
QSUB_DEFAULT = shutil.which("qsub")
if QSUB_DEFAULT is None:
    QSUB_DEFAULT = "qsub"


class PySGEException(Exception):
    """General exception for pysge."""

    def __init__(self, msg="Error in pysge module"):
        """Instantiate class."""
        Exception.__init__(self, msg)


def build_directories(root_dir):
    """Construct subdirectories output, stderr, stdout, and jobs.

    Subdirectories are created in root_dir. The subdirectories
    have the following roles:

    - jobs             Stores the scripts for each job
    - stderr           Stores the stderr output from SGE
    - stdout           Stores the stdout output from SGE
    - output           Stores output (if the scripts place the output here)

    - root_dir   Path to the top-level directory for creation of subdirectories
    """
    # If the root directory doesn't exist, create it
    if not os.path.exists(root_dir):
        os.mkdir(root_dir)

    # Create subdirectories
    directories = [
        os.path.join(root_dir, subdir)
        for subdir in ("output", "stderr", "stdout", "jobs")
    ]
    for dirname in directories:
        os.makedirs(dirname, exist_ok=True)


def build_job_scripts(root_dir, jobs):
    """Construct script for each passed Job in the jobs iterable.

    - jobs          Iterable of jobs
    - root_dir      Path to output directory
    """
    # Loop over the job list, creating each job script in turn, and then adding
    # scriptPath to the Job object
    for job in jobs:
        scriptpath = os.path.join(root_dir, "jobs", job.name)
        with open(scriptpath, "w") as scriptfile:
            scriptfile.write("#!/bin/sh\n#$ -S /bin/bash\n%s\n" % job.script)
        job.scriptpath = scriptpath


def extract_submittable_jobs(waiting):
    """Obtain list of jobs that are able to be submitted from pending list.

    - waiting           List of Job objects
    """
    submittable = set()  # Holds jobs that are able to be submitted
    # Loop over each job, and check all the subjobs in that job's dependency
    # list.  If there are any, and all of these have been submitted, then
    # append the job to the list of submittable jobs.
    for job in waiting:
        unsatisfied = sum([(subjob.submitted is False) for subjob in job.dependencies])
        if unsatisfied == 0:
            submittable.add(job)
    return list(submittable)


def submit_safe_jobs(root_dir, jobs, sgeargs=None):
    """Submit passed list of jobs to SGE server with dir as root for output.

    - root_dir      Path to output directory
    - jobs          Iterable of Job objects
    """
    # Loop over each job, constructing SGE command-line based on job settings
    for job in jobs:
        job.out = shlex.quote(os.path.join(root_dir, "stdout"))
        job.err = shlex.quote(os.path.join(root_dir, "stderr"))

        # Add the job name, current working directory, and SGE stdout/stderr
        # directories to the SGE command line
        args = " -N {} -cwd -o {} -e {} ".format(
            shlex.quote(job.name), job.out, job.err
        )

        # If a queue is specified, add this to the SGE command line
        # LP: This has an undeclared variable, not sure why - delete?
        # if job.queue is not None and job.queue in local_queues:
        #    args += local_queues[job.queue]

        # If the job is actually a JobGroup, add the task numbering argument
        if isinstance(job, JobGroup):
            args += "-t 1:{} ".format(shlex.quote(str(job.tasks)))

        # If there are dependencies for this job, hold the job until they are
        # complete
        if len(job.dependencies) > 0:
            args += "-hold_jid {}".format(
                ",".join([shlex.quote(dep.name) for dep in job.dependencies])
            )

        # Build the qsub SGE commandline (passing local environment)
        qsubcmd = "{} -V {} {}".format(QSUB_DEFAULT, args, shlex.quote(job.scriptpath))
        if sgeargs is not None:
            qsubcmd = "{} {}".format(qsubcmd, shlex.quote(sgeargs))
        safecmd = shlex.split(qsubcmd)
        subprocess.run(safecmd)
        job.submitted = True  # Set the job's submitted flag to True


def submit_jobs(root_dir, jobs, sgeargs=None):
    """Submit passed jobs to SGE server with passed directory as root.

    - root_dir       Path to output directory
    - jobs           List of Job objects
    """
    waiting = list(jobs)  # List of jobs still to be done
    # Loop over the list of pending jobs, while there still are any
    while len(waiting) > 0:
        # extract submittable jobs
        submittable = extract_submittable_jobs(waiting)
        # run those jobs
        submit_safe_jobs(root_dir, submittable, sgeargs)
        # remove those from the waiting list
        for job in submittable:
            waiting.remove(job)


def build_and_submit_jobs(jobs, root_dir=os.curdir, sgeargs=None):
    """Submit passed iterable of Job objects to SGE.

    SGE's output is placed in root_dir
    Additional arguments to SGE are taken as sgeargs

    - jobs       List of Job objects, describing each job to be submitted
    - root_dir   Root directory for SGE and job output
    - sgeargs    Additional arguments to qsub
    """
    # If the passed set of jobs is not a list, turn it into one. This makes the
    # use of a single JobGroup a little more intutitive
    if not isinstance(jobs, list):
        jobs = [jobs]

    # Build and submit the passed jobs
    build_directories(root_dir)  # build all necessary directories
    build_job_scripts(root_dir, jobs)  # build job scripts
    submit_jobs(root_dir, jobs, sgeargs)  # submit the jobs to SGE
