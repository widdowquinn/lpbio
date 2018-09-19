# README.md `pysge`

A module for job submission to SGE-like schedulers

## Getting Started

### Submit a single job

A single command submission to the scheduler requires a `Job` object. This must be defined with a `name` and a `command` (to be run):

```python
from lpbio import pysge

my_job = pysge.Job(name="My_Job", command="echo My Job")

pysge.build_and_submit_jobs(my_job)
```

**NOTE:** jobs are provided to the scheduler by writing them to a jobfile script which has the name of the `Job` object. Therefore to be safe you should avoid passing jobs with identical names, or names containing spaces or other characters that might be problematic for the filesystem. The module will attempt to fix "bad" names, but will not make job names unique. 

### Submit multiple jobs