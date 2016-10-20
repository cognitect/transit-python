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

import sys

PY3 = sys.version_info[0] == 3
PY2 = sys.version_info[0] == 2

if PY3:
  unicode_type = str
  unicode_f = chr
  string_types = [str]
else:
  string_types = [str, unicode]
  unicode_type = unicode
  unicode_f = unichr

isstring = lambda s : type(s) in string_types

if PY3:
  long_type = int
  int_type = int
  int_types = [int]
  number_types = [int, float]
else:
  long_type = long
  int_type = int
  int_types = [long, int]
  number_types = [long, int, float]

isint = lambda i : type(i) in int_types
isnumber = lambda i : type(i) in number_types
isnumber_type = lambda t : t in number_types

if PY3:
  imap = map
  izip = zip
  iteritems = lambda d, **kw: d.items(**kw)
else:
  import itertools
  imap = itertools.imap
  izip = itertools.izip
  iteritems = lambda d, **kw: d.iteritems(**kw)
