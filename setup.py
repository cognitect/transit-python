#!/usr/bin/env python
## Copyright (c) Cognitect, Inc.
## All rights reserved.

from setuptools import setup, find_packages
import subprocess
revision = subprocess.check_output("./bin/revision")

setup(name="transit-python",
      version="0.0."+revision,
      description="Transit marshalling for Python",
      author="Cognitect",
      url="https://github.com/cognitect/transit-python",
      packages=find_packages(),
      install_requires=["python-dateutil", "msgpack-python"])

