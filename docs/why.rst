Why YAtiML?
==============

YAML-based file formats can be very handy, as YAML is easy to write by humans,
and parsing support for it is widely available. Just read your YAML file into a
document structure (a tree of nested dicts and lists), and manipulate that in
your code.

As long as that YAML file contains exactly what you expect, that works fine.
But if it contains a mistake, then you're likely to crash the program with a
cryptic error message, or worse (especially if the YAML file was loaded from the
Internet) it may do something unexpected.

To avoid that, you can validate your YAML using various schema checkers. You
write a description of what your YAML file must look like, then feed that to a
library which checks the incoming file against the description. That gives you a
better error message, but it's a lot of work.

YAtiML takes a different approach. Instead of a schema, you write a Python
class. You probably already know how to do that, so no need to learn anything.
YAtiML then generates loading and dumping functions for you, which convert
between YAML and Python objects. On loading, the input is checked to ensure that
it matches the intended type, using standard Python type annotations on the
class. If there is an error, a (very!) nice error message is produced. Default
values, specified as usual in the ``__init__`` method, are applied
automatically, saving you another big headache.

If you want to go further, and create a more complex YAML-based file format
like Docker Compose-files or the Common Workflow Language, then YAtiML has you
covered too. It lets you hook into the loading and dumping processes, modifying
the formatting of the YAML file without affecting the Python side, which lets
you implement all sorts of nice formatting features. YAtiML supports class
hierarchies, enumerations, and extension points (parts of the YAML document
where anything goes) as well.
