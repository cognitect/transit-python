transit-python
==============

Transit is a format and set of libraries for conveying values between
applications written in different programming languages. The library provides
support for marshalling data to/from Python.

 * [Rationale](http://i-should-be-a-link)
 * [API docs](http://cognitect.github.io/transit-python/)
 * [Specification](http://github.com/cognitect/transit-format)


## Releases and Dependency Information

The [PYPI](https://pypi.python.org/pypi) package is
[`transit-python`](https://pypi.python.org/pypi/transit-python)

 * Latest stable release: [0.8](https://pypi.python.org/pypi/transit-python/0.8)


## Usage

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


## Supported Python versions

 * 2.7.X


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
|big decimal|transit\_types.TaggedValue|float|
|big integer|transit\_types.TaggedValue|long|
|time|long, int, dateutil|long|
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
|tagged value|transit\_types.TaggedValue|transit\_types.TaggedValue|


## Development

### Setup

Transit Python requires Transit to be at the same directory level as
transit-python for access to the exemplar files.


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

Please discuss potential problems or enhancements on the
[transit-format mailing list](https://groups.google.com/forum/#!forum/transit-format).
Issues should be filed using GitHub issues for this project.

Contributing to Cognitect projects requires a signed
[Cognitect Contributor Agreement](http://cognitect.com/contributing).


## Copyright and License

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

