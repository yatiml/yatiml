Recipes
=======

Parsed classes
--------------

For some classes, the easiest way to write them in a YAML file is as a string
representing all the values in the class. For example, you may want to have a
namespaced name that looks like ``ns.subns.name`` in the YAML text format, but
on the Python side represent it as a class having one attribute `namespaces`
that is a list of namespaces, and an attribute `name` that is a string.

To do this, you need to override recognition to tell YAML to recognise a string
(because by default it will expect a mapping), and then to add a savorizing
function that parses the string and generates a mapping, attributes from which
will then be fed to your constructor. In order to save objects of your class as
strings, you'll need to add a sweetening function too. The complete solution
looks like this:

.. literalinclude:: examples/parsed_classes.py
  :caption: ``docs/examples/parsed_classes.py``
  :language: python

The tricky part here is in the savorize and sweeten functions. Savorize needs to
build a list of strings, which YAtiML doesn't help with, so it needs to
construct ruamel.yaml objects directly. For each namespace item, it builds a
``yaml.ScalarNode``, which represents a scalar and has a tag to describe the type,
and a value, a string. It also requires a start and end mark, for which we use
dummy values, as this node was generated and is therefore not in the file. The
ruamel.yaml library will raise an Exception if you do not add those. The item
nodes are then added to a ``yaml.SequenceNode``, and the whole thing set as the
value of the ``namespaces`` attribute.

Sweeten does the reverse of course, getting a list of :class:`yatiml.Node`
objects representing the items in the ``namespaces`` attribute, extracting the
string values using :meth:`yatiml.Node.get_value`, then joining them with
periods and finally combining them with the name. Since we're only altering the
top-level node here, we do not need to build a ``yaml.ScalarNode`` ourselves but
can just use :meth:`yatiml.Node.set_value`.


Timestamps and dates
--------------------

YAML has a `timestamp` type, which represents a point in time. The
`ruamel.yaml` library parses this into a python `datetime.date` object, and
will serialise such an object back to a YAML `timestamp`. YAtiML supports this
as well, so all you need to do to use a timestamp or a date is to use
`datetime.date` in your class definition.

Note that the object created by YAtiML may be an instance of `datetime.date` (if
no time is given) or an instance of `datetime.datetime` (if a time is given)
which is a subclass of `datetime.date`. Since Python does not have a
date-without-time type, you cannot currently specify in the type that you want
only a date, without a time attached to it.

If this is an attribute in a class, and date-with-time is not a legal value,
then you should add a check to the __init__ method that raises an exception if
the given value is an instance of `datetime.datetime`. That way, you can't
accidentally make an instance of the class in Python with an incorrect value
either.


Dashed keys
-----------

Some YAML-based formats (like CFF) use dashes in their mapping keys. This is a
problem for YAtiML, because keys get mapped to parameters of ``__init__``,
which are identifiers, and those are not allowed to contain dashes in Python. So
some kind of conversion will have to be made. YAtiML's seasoning mechanism is
just the way to do it: :class:`yatiml.Node` has two methods to convert all
dashes in a mapping's keys to underscores and back:
:meth:`unders_to_dashes_in_keys()` and :meth:`dashes_to_unders_in_keys()`, so
all you need to do is use underscores instead of dashes when defining your
classes, and add seasoning functions. Here's an example:

.. literalinclude:: examples/dashed_keys.py
  :caption: ``docs/examples/dashed_keys.py``
  :language: python

If you've been paying very close attention, then you may be wondering why this
example passes through the recognition stage. After all, the names of the keys
do not match those of the ``__init__`` parameters. YAtiML is a bit flexible in
this regard, and will match a key to a parameter if it is identical after dashes
have been replaced with underscores. The flexibility is only in the recognition
stage, not in the type checking stage, so you do need the seasoning functions.
(The reason to not completely automate this is that YAtiML cannot know if the
YAML side should have dashes or underscores. So you need to specify this
somehow in order to be able to dump correctly, and then it's better to specify
it on loading as well for symmetry.)


.. _seasoning_enumerations:

Seasoning enumerations
----------------------

By default, YAtiML will use an enum member's name to write to the YAML file, and
that's what it will recognise on loading as well. Sometimes, that's not what you
want however. Maybe you want to use the values, or you want to have the names on
the Python side in uppercase (because PEP-8 says so) while you want to use
a lower-case version in the YAML file. In that case, you can apply YAtiML's
seasoning mechanisms like this:

.. literalinclude:: examples/enum_use_values.py
  :caption: ``docs/examples/enum_use_values.py``
  :language: python

or like this:

.. literalinclude:: examples/enum_lowercase.py
  :caption: ``docs/examples/enum_lowercase.py``
  :language: python
