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

import csv
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


def load_bulk_prokka_config(fname, logger=None):
    """Load bulk_prokka config file into dictionary keyed by filestem"""
    if not os.path.isfile(fname):
        logger.error("Config file %s does not exist; ignoring --config option", fname)
        return None

    # Load config data as a dict of dicts:
    #  top-level: keyed by filestem
    #  inner-level: keyed by header
    with open(fname, "r") as cfh:
        confreader = csv.reader(cfh, delimiter="\t")
        headers = dict([(val, idx) for idx, val in enumerate(next(confreader, None))])
        if "filestem" not in headers:  # Exit if no filestem defined in file
            logger.error(
                "Config file %s lacks 'filestem' header; ignoring --config option",
                fname,
            )
            return None
        confdata = {}  # dict of dicts with config data
        for row in confreader:
            rowdata = {
                header: row[idx]
                for (header, idx) in headers.items()
                if header != "filestem"
            }
            filestem = row[headers["filestem"]]
            if not filestem:
                logger.warning("Skipping row with no filestem:\n\t%s", row)
            else:
                confdata[filestem] = rowdata
    return confdata


def add_prokka_arg(cmd, key, val, logger=None):
    """Add the corresponding prokka argument for key to cmd and return"""
    argdict = {
        "prefix": "--prefix",
        "locustag": "--locustag",
        "increment": "--increment",
        "centre": "--centre",
        "accver": "--accver",
        "kingdom": "--kingdom",
        "genus": "--genus",
        "species": "--species",
        "strain": "--strain",
        "plasmid": "--plasmid",
        "gcode": "--gcode",
        "gram": "--gram",
    }
    if val:
        try:
            cmd = " ".join([cmd, argdict[key], shlex.quote(val)])
        except KeyError:
            logger.warning("Cannot process argument %s (skipping)", key)
    return cmd


def build_prokka_cmd(fname, args, config=None, logger=None):
    """Construct a prokka command-line from the arguments"""
    stem = shlex.quote(os.path.splitext(fname)[0])
    fpath = os.path.join(args.indir, fname)

    cmd = "{} --mincontiglen {} --outdir {}".format(
        shlex.quote(args.prokka_exe),
        shlex.quote(str(args.mincontiglen)),
        shlex.quote(os.path.join(args.outdir, stem)),
    )

    # Process config info
    if config is not None:
        if stem not in config:
            logger.warning(
                "Attempted to process filestem %s, but not found in config file (skipping)",
                stem,
            )
        else:
            for key in config[stem]:
                cmd = add_prokka_arg(cmd, key, config[stem][key], logger)

    if args.compliant:  # Force Genbankk/ENA/DDJB compliance
        cmd = " ".join([cmd, "--compliant"])

    if args.metagenome:  # Improve gene prediction for fragmented genomes
        cmd = " ".join([cmd, "--metagenome"])

    # Add path to input file
    cmd = " ".join([cmd, shlex.quote(fpath)])
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
    """Run main process (i.e. catch command-line) for bulk_prokka script"""
    # If no arguments are passed, parse the command-line
    if argv is None:
        args = parse_cmdline()
    else:
        args = parse_cmdline(argv)
    return run_prokka(args, logger)


def run_prokka(args, logger=None):
    """Run bulk_prokka script"""
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

    # If necessary, load config data for bulk_prokka
    if args.config is not None:
        logger.info("Processing prokka config file %s", args.config)
        config_data = load_bulk_prokka_config(args.config, logger)
        logger.info("Read %d rows from config file", len(config_data))
    else:
        config_data = None

    # Create list of prokka commands
    cmdlist = []
    for fname in infiles:
        cmdlist.append(
            build_prokka_cmd(fname=fname, args=args, config=config_data, logger=logger)
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
