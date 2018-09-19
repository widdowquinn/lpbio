# -*- coding: utf-8 -*-
"""Job class for SGE-like scheduler interactions"""

import os
import shlex
import time

# Base unit of time (s) to wait between polling SGE
SGE_WAIT = 0.01


class Job:
    """Individual job to be run, with list of dependencies."""

    def __init__(self, name, command, queue=None):
        """Instantiate a Job object.

        - name           String describing the job (uniquely)
        - command        String, the valid shell command to run the job
        - queue          String, the SGE queue under which the job shall run
        """
        self.name = shlex.quote(name.replace(" ", "_"))  # Unique name for the job
        self.queue = queue  # The SGE queue to run the job under
        self.command = command  # Command line to run for this job
        self.script = command
        self.scriptPath = None  # Will hold path to the script file
        self.dependencies = []  # List of jobs to be completed first
        self.submitted = False  # Flag: is job submitted?
        self.finished = False

    def add_dependency(self, job):
        """Add passed job to the dependency list for this Job.

        This Job should not execute until all dependent jobs are completed

        - job     Job to be added to the Job's dependency list
        """
        self.dependencies.append(job)

    def remove_dependency(self, job):
        """Remove passed job from this Job's dependency list.

        - job     Job to be removed from the Job's dependency list
        """
        self.dependencies.remove(job)

    def wait(self, interval=SGE_WAIT):
        """Wait until the job finishes, and poll SGE on its status."""
        while not self.finished:
            time.sleep(interval)
            interval = min(2 * interval, 60)
            self.finished = os.system("qstat -j %s > /dev/null" % (self.name))
