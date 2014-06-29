#!/usr/bin/env python
## Copyright (c) Cognitect, Inc.
## All rights reserved.

from setuptools import setup, find_packages

setup(name="transit-python",
      version="0.1",
      description="Transit marshalling for Python",
      author="Cognitect",
      url="https://github.com/cognitect/transit-python",
      packages=find_packages(),
      install_requires=["python-dateutil", "msgpack-python"])

