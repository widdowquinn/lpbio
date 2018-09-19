# -*- coding: utf-8 -*-
"""JobGroup class for SGE-like scheduler interactions"""

import os
import shlex
import time

# Base unit of time (s) to wait between polling SGE
SGE_WAIT = 0.01


class JobGroup:
    """Class that stores a group of jobs, permitting parameter sweeps."""

    def __init__(self, name, command, queue=None, arguments=None):
        """Instantiate a JobGroup object.

        JobGroups allow for the use of combinatorial parameter sweeps by
        using the 'command' and 'arguments' arguments.

        - name              String, the JobGroup name
        - command           String, the command to be run, with arguments
                                    specified
        - queue             String, the queue for SGE to use
        - arguments         Dictionary, the values for each parameter as
                            lists of strings, keyed by an identifier for
                            the command string

        For example, to use a command 'my_cmd' with the arguments
        '-foo' and '-bar' having values 1, 2, 3, 4 and 'a', 'b', 'c', 'd' in
        all combinations, respectively, you would pass
        command='my_cmd $SGE_TASK_ID -foo $fooargs -bar $barargs'
        arguments='{'fooargs': ['1','2','3','4'],
                    'barargs': ['a','b','c','d']}
        """
        self.name = shlex.quote(name.replace(" ", "_"))  # Set JobQueue name
        self.queue = queue  # Set SGE queue to request
        self.command = command  # Set command string
        self.dependencies = []  # Create empty list for dependencies
        self.submitted = False  # Set submitted Boolean
        self.finished = False
        if arguments is not None:
            self.arguments = arguments  # Dictionary of arguments for command
        else:
            self.arguments = {}
        self.generate_script()  # Make SGE script for sweep/array

    def generate_script(self):
        """Create the SGE script that will run the jobs in the JobGroup."""
        self.script = ""  # Holds the script string
        total = 1  # total number of jobs in this group

        # for now, SGE_TASK_ID becomes TASK_ID, but we base it at zero
        self.script += """let "TASK_ID=$SGE_TASK_ID - 1"\n"""

        # build the array definitions
        for key in sorted(self.arguments.keys()):
            # The keys are sorted for py3.5 compatibility with tests
            values = self.arguments[key]
            line = "%s_ARRAY=( " % (key)
            for value in values:
                line += value
                line += " "
            line += " )\n"
            self.script += line
            total *= len(values)
        self.script += "\n"

        # now, build the decoding logic in the script
        for key in sorted(self.arguments.keys()):
            # The keys are sorted for py3.5 compatibility with tests
            count = len(self.arguments[key])
            self.script += """let "%s_INDEX=$TASK_ID %% %d"\n""" % (key, count)
            self.script += """%s=${%s_ARRAY[$%s_INDEX]}\n""" % (key, key, key)
            self.script += """let "TASK_ID=$TASK_ID / %d"\n""" % (count)

        # now, add the command to run the job
        self.script += "\n"
        self.script += self.command
        self.script += "\n"

        # set the number of tasks in this group
        self.tasks = total

    def add_dependency(self, job):
        """Add the passed job to the dependency list for this JobGroup.

        This JobGroup should not execute until all dependent jobs are
        completed

        - job      Job, job to be added to the JobGroup's dependency list
        """
        self.dependencies.append(job)

    def remove_dependency(self, job):
        """Remove passed job from this JobGroup's dependency list.

        - job      Job, job to be removed from the JobGroup's dependency list
        """
        self.dependencies.remove(job)

    def wait(self, interval=SGE_WAIT):
        """Wait for a defined period, then poll SGE for job status."""
        while not self.finished:
            time.sleep(interval)
            interval = min(2 * interval, 60)
            self.finished = os.system("qstat -j %s > /dev/null" % (self.name))
