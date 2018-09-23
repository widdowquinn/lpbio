# -*- coding: utf-8 -*-
"""Module with main code for pyani application/package.

Python package version should match:

r"^__version__ = '(?P<version>[^']+)'$" for setup.py
"""
__version__ = "0.1.0-alpha"

name = "lpbio"

import os
import shlex

from subprocess import check_output, CalledProcessError


class LPBioNotExecutableError(Exception):
    """Exception raised when expected executable is not executable"""

    def __init__(self, msg):
        self.message = msg


def is_exe(filename):
    """Returns True if path is to an executable file

    Use shutil.which() instead?
    """
    filename = shlex.quote(filename)
    if os.path.isfile(filename) and os.access(filename, os.X_OK):
        return True
    else:
        try:
            exefile = check_output(["which", filename]).strip()
        except CalledProcessError:
            raise LPBioNotExecutableError("{0} does not exist".format(filename))
    return os.path.isfile(exefile) and os.access(exefile, os.X_OK)
