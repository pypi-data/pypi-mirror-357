"""Holds all relevant information for packaging and publishing to PyPI."""

from typing import List

import setuptools

# no external requirements of now
requirements: List[str] = []

VERSION = "1.0.0"

# pylint: disable=line-too-long
with open("README.md", "r", encoding="utf-8") as fh_read:
    long_description = fh_read.read()
setuptools.setup(
    name="cztile",
    version=VERSION,
    author="Sebastian Rhode",
    author_email="sebastian.rhode@zeiss.com",
    description="A set of tiling utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Note: Exclude test folder in MANIFEST.in to also remove from source dist
    # See https://stackoverflow.com/questions/8556996/setuptools-troubles-excluding-packages-including-data-files
    # See https://docs.python.org/3.6/distutils/sourcedist.html
    packages=setuptools.find_packages(exclude=["test", "test.*"]),
    license_files=["LICENSE.txt", "NOTICE.txt"],
    # Classifiers help users find your project by categorizing it.
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">3.8,<3.14",
    install_requires=requirements,
)
