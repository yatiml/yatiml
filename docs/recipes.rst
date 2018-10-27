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
`ruamel.yaml` library parses this into a python `datetime.datetime` object, and
will serialise such an object back to a YAML `timestamp`. YAtiML supports this
as well, so all you need to do to use a timestamp or a date is to use
`datetime.datetime` in your class definition.
