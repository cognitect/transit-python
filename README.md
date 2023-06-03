# This library is no longer maintained. An unaffiliated fork exists at https://github.com/3wnbr1/transit-python2.

transit-python
==============

Transit is a format and set of libraries for conveying values between
applications written in different programming languages. The library provides
support for marshalling data to/from Python.

 * [Rationale](http://blog.cognitect.com/blog/2014/7/22/transit)
 * [API docs](http://cognitect.github.io/transit-python/)
  * [Mirrored for PyPI](http://pythonhosted.org/transit-python/)
 * [Specification](http://github.com/cognitect/transit-format)

This implementation's major.minor version number corresponds to the
version of the Transit specification it supports.

_NOTE: Transit is intended primarily as a wire protocol for transferring data between applications. If storing Transit data durably, readers and writers are expected to use the same version of Transit and you are responsible for migrating/transforming/re-storing that data when and if the transit format changes._

## Releases and Dependency Information

The [PYPI](https://pypi.python.org/pypi) package is
[`transit-python`](https://pypi.python.org/pypi/transit-python)

 * Latest stable release: [0.8](https://pypi.python.org/pypi/transit-python)

You can install with any of the following:

 * `easy_install transit-python`
 * `pip install --use-wheel --pre transit-python`

You can uninstall with:

 * `pip uninstall transit-python`

## Usage

```python
# io can be any Python file descriptor,
# like you would typically use with JSON's load/dump

from transit.writer import Writer
from transit.reader import Reader

writer = Writer(io, "json") # or "json-verbose", "msgpack"
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


## Supported Python versions

 * 2.7.X
 * 3.5.X


## Type Mapping

### Typed arrays, lists, and chars

The [transit spec](https://github.com/cognitect/transit-format)
defines several semantic types that map to more general types in Python:

* typed arrays (ints, longs, doubles, floats, bools) map to Python Tuples
* lists map to Python Tuples
* chars map to Strings/Unicode

When the reader encounters an of these (e.g. <code>{"ints" =>
[1,2,3]}</code>) it delivers just the appropriate object to the app
(e.g. <code>(1,2,3)</code>).

Use a TaggedValue to write these out if it will benefit a consuming
app e.g.:

```python
writer.write(TaggedValue("ints", [1,2,3]))
```

### Python's bool and int

In Python, bools are subclasses of int (that is, `True` is actually `1`).

```python
>>> hash(1)
1
>>> hash(True)
1
>>> True == 1
True
```

This becomes problematic when decoding a map that contains bool and
int keys.  The bool keys may be overridden (ie: you'll only see the int key),
and the value will be one of any possible bool/int keyed value.

```python
>>> {1: "Hello", True: "World"}
{1: 'World'}
```

To counter this problem, the latest version of Transit Python introduces a
Boolean type with singleton (by convention of use) instances of "true" and
"false." A Boolean can be converted to a native Python bool with bool(x) where
x is the "true" or "false" instance. Logical evaluation works correctly with
Booleans (that is, they override the __nonzero__ method and correctly evaluate
as true and false in simple logical evaluation), but uses of a Boolean as an
integer will fail.

### Default type mapping

|Transit type|Write accepts|Read returns|
|------------|-------------|------------|
|null|None|None|
|string|unicode, str|unicode|
|boolean|bool|bool|
|integer|int|int|
|decimal|float|float|
|keyword|transit\_types.Keyword|transit\_types.Keyword|
|symbol|transit\_types.Symbol|transit\_types.Symbol|
|big decimal|float|float|
|big integer|long|long|
|time|long, int, datetime|datetime|
|uri|transit\_types.URI|transit\_types.URI|
|uuid|uuid.UUID|uuid.UUID|
|char|transit\_types.TaggedValue|unicode|
|array|list, tuple|tuple|
|list|list, tuple|tuple|
|set|set|set|
|map|dict|dict|
|bytes|transit\_types.TaggedValue|tuple|
|shorts|transit\_types.TaggedValue|tuple|
|ints|transit\_types.TaggedValue|tuple|
|longs|transit\_types.TaggedValue|tuple|
|floats|transit\_types.TaggedValue|tuple|
|doubles|transit\_types.TaggedValue|tuple|
|chars|transit\_types.TaggedValue|tuple|
|bools|transit\_types.TaggedValue|tuple|
|link|transit\_types.Link|transit\_types.Link|


## Development

### Setup

Transit Python requires [Transit](http://github.com/cognitect/transit-format) to be at the same directory level as
transit-python for access to the exemplar files. You will also need
to add transit-python to your PYTHONPATH.

```sh
export PYTHONPATH=$(pwd)
```

Tests should be run from the transit-python directory.

### Benchmarks

```sh
python tests/seattle_benchmark.py
```

### Running the examples

```sh
python tests/exemplars_test.py
```

### Build

```sh
pip install -e .
```

The version number is automatically incremented based on the number of commits.
The command below shows what version number will be applied.

```sh
bin/revision
```


## Contributing

This library is open source, developed internally by Cognitect. We welcome discussions of potential problems and enhancement suggestions on the [transit-format mailing list](https://groups.google.com/forum/#!forum/transit-format). Issues can be filed using GitHub [issues](https://github.com/cognitect/transit-python/issues) for this project. Because transit is incorporated into products and client projects, we prefer to do development internally and are not accepting pull requests or patches.

## Copyright and License

Copyright © 2014-2016 Cognitect

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
