#!/usr/bin/env python
## Copyright (c) Cognitect, Inc.
## All rights reserved.

from distutils.core import setup

setup(name="transit-python",
      version="0.1",
      description="Transit marshalling for Python",
      author="Cognitect",
      url="https://github.com/cognitect/transit-python",
      packages=["distutils", "python-dateutil", "msgpack-python"])