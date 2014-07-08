transit-python
==============

Transit is a format and set of libraries for conveying values between
applications written in different programming languages. See
[https://github.com/cognitect/transit-format](https://github.com/cognitect/transit-format)
for details.

transit-python is a Transit encoder/decoder library for Python.

```python
# io can be any Python file descriptor,
# like you would typical use with JSON's load/dump

from transit.writer import Writer
from transit.reader import Reader

writer = Writer("json", io) # or "json-verbose", "msgpack"
writer.write(value)

reader = Reader("json") # or "msgpack"
val = reader.read(io)
```

For example:

```
>>> from transit.writer import Writer
>>> from transit.reader import Reader
>>> from StringIO import StringIO
>>> io = StringIO()
>>> writer = Writer(io, "json")
>>> writer.write(["abc", 1234567890])
>>> s = io.getvalue()
>>> reader = Reader()
>>> vals = reader.read(StringIO(s))
```

# Typed arrays, lists, and chars

The [transit spec](https://github.com/cognitect/transit-format)
defines several semantic types that map to more general types in Python:

* typed arrays (ints, longs, doubles, floats, bools) map to Python Tuples
* lists map to Python Tuples
* chars map to Strings

When the reader encounters an of these (e.g. <code>{"ints" =>
[1,2,3]}</code>) it delivers just the appropriate object to the app
(e.g. <code>[1,2,3]</code>).

Use a TaggedValue to write these out if it will benefit a consuming
app e.g.:

```python
writer.write(TaggedValue("ints", [1,2,3]))
```

# Supported Python versions

 * 2.7.X

# Development

## Setup

Transit Python requires Transit to be at the same directory level as
transit-python for access to the exemplar files.


## Benchmarks

```sh
python tests/seattle_benchmark.py
```

## Running the examples

```sh
python tests/exemplars_test.py
```

## Build

```sh
pip install -e .
```

The version number is automatically incremented based on the number of commits.
The command below shows what version number will be applied.

```sh
bin/revision
```

# Copyright and License

Copyright © 2014 Cognitect

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

