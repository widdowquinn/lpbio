# README.md `pysge`

A module for job submission to SGE-like schedulers

<!-- TOC -->

- [Getting Started](#getting-started)
    - [Submit a single job](#submit-a-single-job)
    - [Submit multiple single jobs](#submit-multiple-single-jobs)
    - [Submit a parameter sweep job](#submit-a-parameter-sweep-job)
    - [Submit jobs with dependencies](#submit-jobs-with-dependencies)

<!-- /TOC -->

## Getting Started

### Submit a single job

A single command submission to the scheduler requires a `Job` object. This must be defined with a `name` and a `command` (to be run):

```python
from lpbio import pysge

my_job = pysge.Job(name="My_Job", command="echo My Job")

pysge.build_and_submit_jobs(my_job)
```

> **NOTE:** jobs are provided to the scheduler by writing them to a jobfile script which has the name of the `Job` object. Therefore to be safe you should avoid passing jobs with identical names, or names containing spaces or other characters that might be problematic for the filesystem. The module will attempt to fix "bad" names, but will not make job names unique.

### Submit multiple single jobs

To submit multiple single jobs to the scheduler, you can pass a list of `Job` objects to `build_and_submit_jobs()`:

```python
from lpbio import pysge

job1 = pysge.Job(name="My_Job_1", command="echo My Job 1")
job2 = pysge.Job(name="My_Job_2", command="echo My Job 2")

pysge.build_and_submit_jobs([my_job1, my_job2])
```

### Submit a parameter sweep job

To submit a job which varies the same command by *sweeping* parameters (passing each of a set of parameter choices in turn), use a `JobGroup` object. The arguments to be passed (in turn) are provided as a dictionary, keyed by the variable name to be used in the SGE script. This variable name needs to be present in your passed `command`:

```python
from lpbio import pysge

my_jobgroup = pysge.JobGroup(name="My_JobGroup", command="echo $my_arg",
                             arguments={"my_arg": (1, 2, 3, 4, 5)})
pysge.build_and_submit_jobs(my_jobgroup)
```

To sweep multiple parameters in all combinations, provide more than one keyed set of values as `arguments`:

```python
from lpbio import pysge

my_jobgroup = pysge.JobGroup(name="My_JobGroup", command="echo $my_arg",
                             arguments={"my_arg_1": (1, 2, 3, 4, 5),
                                        "my_arg_2": ("a", "b", "c")})
pysge.build_and_submit_jobs(my_jobgroup)
```

### Submit jobs with dependencies

If jobs must be run in strict order, for example if `job1` must complete before `job2` can be run, then add `job2` as a dependency to `job1`, as follows:

```python
from lpbio import pysge

job1 = pysge.Job(name="My_Job_1", command="echo My Job 1")
job2 = pysge.Job(name="My_Job_2", command="echo My Job 2")

job1.add_dependency(job2)

pysge.build_and_submit_jobs([my_job1, my_job2])
```

> **NOTE:** you must pass all jobs and dependencies to the scheduler, otherwise your process will hang.