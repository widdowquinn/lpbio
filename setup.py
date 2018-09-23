# try using distribute or setuptools or distutils.
try:
    import distribute_setup

    distribute_setup.use_setuptools()
except ImportError:
    pass

import setuptools

import os
import sys
import re

# Get long description from README.md
with open("README.md", "r") as dfh:
    long_description = dfh.read()

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

setuptools.setup(
    name="lpbio",
    version=version,
    author="Leighton Pritchard",
    author_email="leighton.pritchard@hutton.ac.uk",
    description="lpbio provides scripts and modules for computational biology",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="genome bioinformatics sequence",
    platforms="Posix; MacOS X",
    url="http://widdowquinn.github.io/lpbio/",  # project home page
    download_url="https://github.com/widdowquinn/lpbio/releases",
    scripts=[os.path.join("bin", "bulk_prokka")],
    packages=setuptools.find_packages(),
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
