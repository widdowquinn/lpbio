# -*- coding: utf-8 -*-
"""Parser for bulk_prokka script

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

import sys

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from ..prokka_script import __version__


def parse_cmdline(argv=None):
    """Parse command line for bulk_prokka script"""
    parser = ArgumentParser(
        prog="bulk_prokka ({})".format(__version__),
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    # Required position arguments
    parser.add_argument(
        action="store", dest="indir", default=None, help="input directory"
    )
    parser.add_argument(
        action="store", dest="outdir", default=None, help="output directory"
    )

    # Common arguments
    parser.add_argument(
        "-l",
        "--logfile",
        dest="logfile",
        action="store",
        default=None,
        help="logfile location",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        help="report verbose progress to log",
    )
    parser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        default=False,
        help="force deletion of previous output directory",
    )
    parser.add_argument(
        "--extensions",
        dest="extensions",
        action="store",
        default="fas,fasta,fna,fa",
        help="allowed input file extensions",
    )

    # Prokka-specific arguments
    parser.add_argument(
        "--config",
        action="store",
        dest="config",
        default=None,
        help="path to config file for bulk_prokka run"
    )
    parser.add_argument(
        "--prokka_exe",
        action="store",
        dest="prokka_exe",
        default="prokka",
        help="path to prokka executable",
    )
    parser.add_argument(
        "--compliant",
        action="store_true",
        dest="compliant",
        default=False,
        help="Force Genbank/ENA/DDJB compliance",
    )
    parser.add_argument(
        "--metagenome",
        action="store_true",
        dest="metagenome",
        default=False,
        help="Improve gene prediction for fragmented genomes",
    )
    parser.add_argument(
        "--mincontiglen",
        action="store",
        dest="mincontiglen",
        default=200,
        help="Improve gene prediction for fragmented genomes",
    )

    # Scheduler arguments
    parser.add_argument(
        "--scheduler",
        dest="scheduler",
        action="store",
        default="multiprocessing",
        choices=["multiprocessing", "SGE"],
        help="Job scheduler (default multiprocessing, i.e. locally)",
    )
    parser.add_argument(
        "--workers",
        dest="workers",
        action="store",
        default=None,
        type=int,
        help="Number of worker processes for multiprocessing "
        "(default zero, meaning use all available cores)",
    )
    parser.add_argument(
        "--SGEgroupsize",
        dest="sgegroupsize",
        action="store",
        default=10000,
        type=int,
        help="Number of jobs to place in an SGE array group (default 10000)",
    )
    parser.add_argument(
        "--SGEargs",
        dest="sgeargs",
        action="store",
        default=None,
        type=str,
        help="Additional arguments for qsub",
    )
    parser.add_argument(
        "--jobprefix",
        dest="jobprefix",
        action="store",
        default="PROKKA_BULK",
        help="Prefix for SGE jobs (default PROKKA_BULK).",
    )

    # Parse inputs
    if argv is None:
        argv = sys.argv[1:]

    return parser.parse_args(argv)
