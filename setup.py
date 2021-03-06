#!/usr/bin/env python

import os
import re

from setuptools import setup


def _get_version():
    """Get the version but do not import the package."""
    with open(os.path.join(os.path.dirname(__file__), 'bomberman', 'version.py')) as version_file:
        return re.compile(r"^__version__ = '(.*?)'", re.S).match(version_file.read()).group(1)

setup(version=_get_version())
