# -*- coding: utf-8 -*-
"""Implements the bulk_prokka script for annotating genomes

(c) The James Hutton Institute 2018
Author: Leighton Pritchard

Contact: leighton.pritchard@hutton.ac.uk

Leighton Pritchard,
Information and Computing Sciences,
James Hutton Institute,
Errol Road,
Invergowrie,
Dundee,
DD2 5DA,
Scotland,
UK

The MIT License

Copyright (c) 2018 The James Hutton Institute

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import multiprocessing
import os
import shlex
import shutil
import subprocess
import sys
import time

import pysge

from .. import __version__
from .logger import build_logger
from .parsers.prokka_parser import parse_cmdline


def identify_inputs(args, logger):
    """Return True if input directory exists and contains files"""
    if not os.path.isdir(args.indir):
        logger.error("Input directory %s does not exist", args.indir)
        return False
    infiles = [
        fname
        for fname in os.listdir(args.indir)
        if os.path.splitext(fname)[-1] in args.extensions
    ]
    if not len(infiles):
        logger.error(
            "Input directory %s contains no files with extension in %s",
            args.indir,
            args.extensions,
        )
    logger.info(
        "Input directory %s exists and contains %d files with extension in %s",
        args.indir,
        len(infiles),
        args.extensions,
    )
    return infiles


def build_prokka_cmd(
    fname, indir, outdir, prokka_exe, locustag=None, prefix=None, logger=None
):
    """Construct a prokka command-line from the arguments"""
    stem = os.path.splitext(fname)[0]
    fpath = os.path.join(indir, fname)
    if locustag is None:
        logger.debug("No locus tag provided for %s: using %s", fpath, stem)
        locustag = stem
    if prefix is None:
        logger.debug("No prefix provided for %s: using %s", fpath, stem)
        prefix = stem
    cmd = "{} --locustag {} --outdir {} --prefix {} {}".format(
        shlex.quote(prokka_exe),
        shlex.quote(locustag),
        shlex.quote(os.path.join(outdir, stem)),
        shlex.quote(prefix),
        shlex.quote(fpath),
    )
    logger.info("\t%s", cmd)
    return cmd


def run_multiprocessing(cmdlist, args, logger):
    """Run the commands in the list with multiprocessing"""
    if not args.workers:
        logger.info("Using maximum number of multiprocessing worker threads")
    else:
        logger.info("Using %d multiprocessing worker threads", args.workers)

    pool = multiprocessing.Pool(processes=args.workers)
    results = [
        pool.apply_async(
            subprocess.run,
            (cline,),
            {
                "shell": sys.platform != "win32",
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
            },
        )
        for cline in cmdlist
    ]
    pool.close()
    pool.join()
    return results


def run_sge(cmdlist, args, logger):
    """Run the commands in the list with SGE"""
    logger.debug("Converting command-lines to Job objects")
    joblist = []
    for idx, cline in enumerate(cmdlist):
        joblist.append(pysge.Job(name="prokka_job_{}".format(idx), command=cline))
    pysge.build_and_submit_jobs(joblist)


def run_main(argv=None, logger=None):
    """Run main process for bulk_prokka script"""
    # If no arguments are passed, parse the command-line
    if argv is None:
        args = parse_cmdline()
    else:
        args = parse_cmdline(argv)

    # Set up logging
    time0 = time.time()
    if logger is None:
        logger = build_logger("bulk_prokka ({})".format(__version__), args)

    # Check prokka exists
    if not shutil.which(args.prokka_exe):
        logger.error("Prokka executable %s is not found (exiting)", args.prokka_exe)
        return 1

    # Process arguments
    args.extensions = {".{}".format(ext) for ext in args.extensions.split(",")}

    # Identify input genomes
    infiles = identify_inputs(args, logger)
    if not infiles:
        logger.error("Could not find input (exiting)")
        return 1

    # Can the output directory be made
    if os.path.isdir(args.outdir):
        if not args.force:
            logger.error(
                "Cannot use existing directory %s for prokka output (exiting)",
                args.outdir,
            )
            return 1
        else:
            logger.warning(
                "Removing output directory %s and everything under it", args.outdir
            )
            shutil.rmtree(args.outdir)

    # Create list of prokka commands
    cmdlist = []
    for fname in infiles:
        cmdlist.append(
            build_prokka_cmd(
                fname=fname,
                indir=args.indir,
                outdir=args.outdir,
                prokka_exe=args.prokka_exe,
                locustag=args.locustag,
                prefix=args.prefix,
                logger=logger,
            )
        )
    logger.info("Compiled %d prokka command-lines", len(cmdlist))

    # Submit commands to scheduler
    logger.info("Submitting prokka command-lines to %s scheduler", args.scheduler)
    if args.scheduler == "multiprocessing":
        run_multiprocessing(cmdlist, args, logger)
        # To extract more information on each run, use
        # [result.get() for result in results]
    if args.scheduler == "SGE":
        run_sge(cmdlist, args, logger)
    logger.info("Submission complete")

    # Report on clean exit
    logger.info("Completed. Time taken: {:.2f}".format(time.time() - time0))
    return 0
