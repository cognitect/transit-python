#!/usr/bin/env python

## Copyright 2014 Cognitect. All Rights Reserved.
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS-IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

from setuptools import setup, find_packages
import subprocess
revision = subprocess.check_output("./bin/revision")

setup(name="transit-python",
      version="0.1."+revision,
      description="Transit marshalling for Python",
      author="Cognitect",
      url="https://github.com/cognitect/transit-python",
      packages=find_packages(),
      install_requires=["python-dateutil", "msgpack-python"])

