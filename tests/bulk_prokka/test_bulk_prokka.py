# -*- coding: utf-8 -*-
"""Tests of bulk_prokka script"""

import logging
import os
import shlex
import shutil
import subprocess
import unittest

from argparse import Namespace

import pytest  # noqa: E0401

from lpbio import pysge

from lpbio.scripts import prokka_script  # noqa: E0401

# Null logger to enable tests of functions expecting a logger
NULL_LOGGER = logging.getLogger("test_bulk_prokka.py null logger")

# Globals for namespaces
PROKKA_EXE = "prokka"


def get_prokka_version(prokka_exe):
    """Returns string describing the PROKKA version number

    PROKKA databases vary between minor versions, so tests may fail where
    output is database-dependent and we're comparing output to determine correct operation
    """
    args = [shlex.quote(prokka_exe), "--version"]
    pipe = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return pipe.stderr.strip().split()[-1].decode("utf-8")


TESTDIR = os.path.join("tests", "bulk_prokka")
INDIR = os.path.join(TESTDIR, "input")
OUTDIR = os.path.join(TESTDIR, "output")
TARGETDIR = os.path.join(TESTDIR, "targets", get_prokka_version(PROKKA_EXE))
FAKE_INDIR = os.path.join(TESTDIR, "nodir")  # Path should not exist
EXTENSIONS = {".fas", ".fasta", ".fna", ".fa"}
EXTENSIONS_STR = "fas,fna,fasta,fa"
CONFIG_FNAME = os.path.join(TESTDIR, "prokka_conf.tab")
MINCONTIGLEN = 200
COMPLIANT = False
METAGENOME = False

# Namespaces for tests
VALID_INDIR = Namespace(
    indir=INDIR,
    extensions=EXTENSIONS,
    prokka_exe=PROKKA_EXE,
    mincontiglen=MINCONTIGLEN,
    outdir=OUTDIR,
    compliant=COMPLIANT,
    metagenome=METAGENOME,
    config=CONFIG_FNAME,
)
MISSING_INDIR = Namespace(
    indir=FAKE_INDIR,
    extensions=EXTENSIONS,
    prokka_exe=PROKKA_EXE,
    mincontiglen=MINCONTIGLEN,
    outdir=OUTDIR,
    compliant=COMPLIANT,
    metagenome=METAGENOME,
    config=CONFIG_FNAME,
)
AS_SCRIPT_MP = Namespace(
    indir=INDIR,
    extensions=EXTENSIONS_STR,
    prokka_exe=PROKKA_EXE,
    mincontiglen=MINCONTIGLEN,
    outdir=OUTDIR,
    compliant=COMPLIANT,
    metagenome=METAGENOME,
    config=CONFIG_FNAME,
    scheduler="multiprocessing",
    workers=8,
    force=True,
)
AS_SCRIPT_SGE = Namespace(
    indir=INDIR,
    extensions=EXTENSIONS_STR,
    prokka_exe=PROKKA_EXE,
    mincontiglen=MINCONTIGLEN,
    outdir=OUTDIR,
    compliant=COMPLIANT,
    metagenome=METAGENOME,
    config=CONFIG_FNAME,
    scheduler="SGE",
    force=True,
)


# Values to test against
INFILENAMES = [
    "GCF_000183385.1_ASM18338v1_genomic.fna",
    "GCF_000219375.1_ASM21937v1_genomic.fna",
    "GCF_000270525.1_ASM27052v1_genomic.fna",
]
CONFDATA = {
    "GCF_000183385.1_ASM18338v1_genomic": {
        "prefix": "GCF_000183385",
        "locustag": "GCF_000183385",
        "increment": "1",
        "centre": "NCBI",
        "accver": "1",
        "kingdom": "Bacteria",
        "genus": "Mycoplasma",
        "species": "bovis",
        "strain": "PG45",
        "plasmid": "",
        "gcode": "11",
    },
    "GCF_000219375.1_ASM21937v1_genomic": {
        "prefix": "GCF_000219375",
        "locustag": "GCF_000219375",
        "increment": "5",
        "centre": "BGI",
        "accver": "1",
        "kingdom": "Bacteria",
        "genus": "Mycoplasma",
        "species": "bovis",
        "strain": "Hubei-1",
        "plasmid": "",
        "gcode": "11",
    },
    "GCF_000270525.1_ASM27052v1_genomic": {
        "prefix": "GCF_000270525",
        "locustag": "GCF_000270525",
        "increment": "10",
        "centre": "JHI",
        "accver": "1",
        "kingdom": "Bacteria",
        "genus": "Mycoplasma",
        "species": "bovis",
        "strain": "HB0801",
        "plasmid": "",
        "gcode": "11",
    },
}
PROKKA_CMD = " ".join(
    [
        "prokka",
        "--mincontiglen 200",
        "--outdir tests/bulk_prokka/output/GCF_000183385.1_ASM18338v1_genomic",
        "--accver 1",
        "--centre NCBI",
        "--gcode 11",
        "--genus Mycoplasma",
        "--increment 1",
        "--kingdom Bacteria",
        "--locustag",
        "GCF_000183385",
        "--prefix GCF_000183385",
        "--species bovis",
        "--strain PG45",
        "tests/bulk_prokka/input/GCF_000183385.1_ASM18338v1_genomic.fna",
    ]
)
# For output file checks, we try to avoid anything with a date (this will not
# match to the targets, or expected not to be constant between runs. For instance
# GFF file attributes may not be ordered between runs
OUTFILES = {
    "GCF_000183385.1_ASM18338v1_genomic": (
        "GCF_000183385.faa",
        "GCF_000183385.ffn",
        "GCF_000183385.fna",
    ),
    "GCF_000219375.1_ASM21937v1_genomic": (
        "GCF_000219375.faa",
        "GCF_000219375.ffn",
        "GCF_000219375.fna",
    ),
    "GCF_000270525.1_ASM27052v1_genomic": (
        "GCF_000270525.faa",
        "GCF_000270525.ffn",
        "GCF_000270525.fna",
    ),
}


class TestBulkProkka(unittest.TestCase):

    """Class collecting tests for bulk_prokka script."""

    def check_outputs(self):
        """Test whether the output files are the same, when run."""
        for key, fnames in OUTFILES.items():
            tdir = os.path.join(TARGETDIR, key)
            odir = os.path.join(OUTDIR, key)
            for fname in fnames:
                with open(os.path.join(odir, fname), "r") as ofh:
                    with open(os.path.join(tdir, fname), "r") as tfh:
                        self.assertEqual(ofh.read(), tfh.read())

    def test_identify_inputs(self):
        """Input directory exists and contains files"""
        # Correctly reads valid files
        infiles = prokka_script.identify_inputs(VALID_INDIR, NULL_LOGGER)
        self.assertEqual(sorted(infiles), sorted(INFILENAMES))
        # Correctly returns empty if no input found
        infiles = prokka_script.identify_inputs(MISSING_INDIR, NULL_LOGGER)
        self.assertFalse(infiles)

    def test_config_load(self):
        """Loads and parses bulk_prokka config file"""
        confdata = prokka_script.load_bulk_prokka_config(CONFIG_FNAME, NULL_LOGGER)
        self.assertEqual(confdata, CONFDATA)

    def test_build_prokka_cmd(self):
        """Builds PROKKA command from args and config data"""
        cmd = prokka_script.build_prokka_cmd(
            INFILENAMES[0], VALID_INDIR, CONFDATA, NULL_LOGGER
        )
        self.assertEqual(cmd, PROKKA_CMD)

    def test_script_run_mp(self):
        """Runs script with multiprocessing"""
        retval = prokka_script.run_prokka(AS_SCRIPT_MP, NULL_LOGGER)
        self.assertEqual(retval, 0)
        self.check_outputs()

    @pytest.mark.skipif(
        shutil.which(pysge.QSUB_DEFAULT) is None,
        reason="qsub executable ({}) could not be found".format(pysge.QSUB_DEFAULT),
    )
    def test_script_run_sge(self):
        """Run script with SGE"""
        retval = prokka_script.run_prokka(AS_SCRIPT_SGE, NULL_LOGGER, wait=True)
        self.assertEqual(retval, 0)
        self.check_outputs()
