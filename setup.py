#!/usr/bin/env python

import os

from setuptools import setup


root_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(root_dir, "README.rst")) as f:
    long_description = f.read()

setup(
    name="aio-wsio",
    version="0.1a1",
    description=("asyncio implementation of an event-based "
                 "library similar to Socket.IO"),
    long_description=long_description,
    author="Alexander Elvers",
    license="MIT",
    packages=["aiowsio"],
    include_package_data=True,
    install_requires=[
        "websockets",
    ],
)
