# try using distribute or setuptools or distutils.
try:
    import distribute_setup

    distribute_setup.use_setuptools()
except ImportError:
    pass

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os
import sys
import re

# parse version from package/module without importing or
# evaluating the code
vfname = os.path.join("lpbio", "__init__.py")
with open(vfname, "r") as fh:
    for line in fh:
        print(line)
        m = re.search(r"^__version__ = [\"'](?P<version>.*)[\"']$", line)
        if m:
            version = m.group("version")
            break

if sys.version_info <= (3, 0):
    sys.stderr.write("ERROR: lpbio requires Python 3 " + "or above...exiting.\n")
    sys.exit(1)

setup(
    name="lpbio",
    version=version,
    author="Leighton Pritchard",
    author_email="leighton.pritchard@hutton.ac.uk",
    description="".join(
        ["lpbio provides scripts and modules for computational biology"]
    ),
    license="MIT",
    keywords="genome bioinformatics sequence",
    platforms="Posix; MacOS X",
    url="http://widdowquinn.github.io/lpbio/",  # project home page
    download_url="https://github.com/widdowquinn/lpbio/releases",
    scripts=[],
    packages=["lpbio"],
    package_data={},
    include_package_date=True,
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
