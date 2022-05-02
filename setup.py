#!/usr/bin/env python3

import os
import glob
import shutil
from setuptools import setup, Command
import distutils.cmd
import distutils.log
import setuptools
import subprocess

# get key package details from py_pkg/__version__.py
about = {}  # type: ignore
here = os.path.abspath(os.path.dirname(__file__))

class PyTestCommand(distutils.cmd.Command):
    """A custom command to run Pylint on all Python source files."""

    description = 'Run pytest tests'
    user_options = [

    ]

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        pass

    def finalize_options(self):
        """Post-process options."""
        pass

    def run(self):
        """Run command."""
        command = [
            'pytest --full-trace --verbose --color=yes --disable-pytest-warnings --no-summary --pyargs tests']

        self.announce(
            'Running command: %s' % str(command),
            level=distutils.log.INFO)
        subprocess.Popen(command, shell=True)

# package configuration - for reference see:
# https://setuptools.readthedocs.io/en/latest/setuptools.html#id9
setup(
    packages=['examples'],
    include_package_data=True,
    python_requires=">=3.9.*",
    install_requires=[
        'pytest'
    ],
    cmdclass={
        'test': PyTestCommand
    },
    zip_safe=False,
    entry_points={
       
    }
)
