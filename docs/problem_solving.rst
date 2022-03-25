Problem solving
===============

This section collects some useful information about solving problems you may
encounter when working with YAtiML.

Enabling logging
----------------

YAtiML uses the standard Python logging system, using a logger named ``yatiml``.
YAtiML produces log messages at the INFO and DEBUG levels, which makes them
invisible at Python's default log level of WARNING. To be able to see what
YAtiML does, you can either lower the general Python log level (which may cause
other parts of your program to produce (more) log output as well), or you can
lower YAtiML's log level specifically. To do the latter, use this:

.. code-block:: python

  import logging
  import yatiml

  yatiml.logger.setLevel(logging.INFO)

Or you can use ``logging.DEBUG`` for very detailed output.

It seems that you may have to do a ``logging.debug()`` call to get any output at
all, maybe because that causes Python to set up something it needs. There's
probably a good explanation and a better fix for this. If you know, please
contribute.

In order to understand how to interpret the output, it helps to have an idea of
how YAtiML processes a YAML file into Python objects. See `The YAtiML
pipeline`_ below for more on that.

Unions with bool
----------------

While defining your classes, you may want to have an attribute that can be of
multiple types. As described in the tutorial, you would use a ``Union`` for
this. For example something like

.. code-block:: python

  class Setting:
      def __init__(name: str,
                   value: Union[str, int, float, bool]
                   ) -> None:
          self.name = name
          self.value = value

is likely to occur in many YAML-based configuration file formats.

There is a problem with the above code, in that it will give an error message if
you try to read the following input on Python < 3.7, saying that it could not
recognise the bool value:

.. code-block:: yaml

  name: test
  value: true

(Scroll down for the fix, if you don't care for the explanation.)

Arguably, this is a bug in Python's type handling, and the developers of
Python's ``typing`` module seem to agree, because they have fixed this in Python
3.7. What happens here is that in Python, ``bool`` is a subtype of ``int``, in
other words, any ``bool`` value is also an ``int`` value. Furthermore, the
``Union`` class will automatically normalise the types it is passed by removing
redundant types. If you put in a type twice then one copy will be removed for
instance, and also, if you put in a type and also a subtype of that type, then
the subtype will be removed. This makes some sense: if every ``bool`` is an
``int``, then just ``int`` will already match boolean values, and ``bool`` is
redundant.

While this works for Python, it's problematic in YAML, where ``bool`` and
``int`` are unrelated types. Indeed, YAtiML will not accept a boolean value in
the YAML file if you declare the attribute to be an ``int``. And that's where
we get into trouble: Python normalises the above Union to ``Union[str, int,
float]``, and YAtiML reads this and generates an error if you feed it a boolean.

In Python 3.7, the behaviour of Union has changed. While mypy still does the
normalisation internally when checking types, the runtime Union object no longer
normalises. Since the runtime object is what YAtiML reads, this problem does
not occur on Python 3.7 (and hopefully versions after that, the `typing` module
is not entirely stable yet).

A fix for Python < 3.7
''''''''''''''''''''''

So, this is fixed in Python 3.7, but what if you're running on an older version?
In that case you need a work-around, and YAtiML provides one called
``bool_union_fix``. It works like this:

.. code-block:: python

  from yatiml import bool_union_fix

  class Setting:
      def __init__(name: str,
                   value: Union[str, int, float, bool, bool_union_fix]
                   ) -> None:
          self.name = name
          self.value = value

All you need to do is import ``bool_union_fix`` and add it to the list of types
in the ``Union``, and now things will work as expected (also in Python 3.7).

``bool_union_fix`` is essentially a dummy type that is recognised by YAtiML and
treated just like ``bool``. Since it's a separate type, it isn't merged into the
``int``, so it'll still be there for YAtiML to read. Note that you do need the
``bool`` in there as well, to avoid mypy complaining if you try to create a
Setting object in your code with a bool for the value attribute.


The YAtiML pipeline
-------------------

With plain PyYAML or ruamel.yaml, the loading process has two stages. First, the
text is parsed into a parse tree, which consists of nodes. Each node has a tag
and a value. Second, objects are constructed from the nodes, with the type of
the object decided based on the tag, and the contents of the object coming from
the value.

YAtiML inserts three additional stages in between the two existing ones:
recognition, savourising, and type checking.

Recognition determines, for each node, as which type YAtiML will try to process
it. This is mostly based on the object model given to the custom loader. In our
ongoing example, the value corresponding to the ``name`` attribute is expected
to be a string, so YAtiML will try to recognise only a string here. The ``age``
attribute has a union type, and for those YAtiML will look at the value given
and see if it matches one of the types in the union. If it matches exactly one,
it is recognised as that type. If it matches none of them, or multiple, an error
message is given.

When recognising a node that according to the object model is of a custom class
type, YAtiML will try to recognise a mapping node with keys and values according
to the custom class's ``__init__`` method's parameters. If the custom class has
subclasses which are also registered with the loader, then those will be
recognised as well at this point in the document. If both a class and its
subclass are matched, the node is recognised as being of the subclass, i.e.
the recognition process prefers the most derived class. If there are multiple
matching sibling subclasses, the node is declared ambiguous and an error is
raised. Recognition for a custom class can be overridden using a
``_yatiml_recognize()`` method.

Incidentally, a technical term for what the recognition process does is `type
inference`, which explains the name YAtiML: it inserts type inference in the
middle of the YAML processing pipeline.

The second and third stages, savourising and type checking, only apply to custom
classes. To savourise a recognised node, YAtiML calls that node's
``_yatiml_savorize()`` method, after calling those of its base classes, if any.
Savourising is entirely defined by the custom class, the default is to do
nothing. After savourising, the resulting mapping is type checked against the
``__init__`` signature, since Python does not do run-time type checking itself.
This is a safety feature, since the read-in YAML document will often be
untrusted, or if it is, at least a convenience feature, in that what you see in
the ``__init__`` signature is guaranteed to be what you get, thus applying the
principle of least surprise.

Note that no type check is done for built-in types, but for built-in types the
default recognition process is effectively a type check, and it cannot be
overridden. Another way of looking at the type check for custom classes is that
it reduces the requirements on custom recognition functions: they need to merely
disambiguate between derived classes and in unions, rather than performing a
complete type check. That makes it easier to write them.

Error messages
--------------

This section contains some error messages that you may encounter when using
YAtiML, and potential solutions to try if you do. If you run into an error that
you cannot figure out, please make an issue describing the error message and
what you are doing (a short example really helps!). Contributions directly to
the documentation are of course also welcome! See the
:ref:`development` section for information on how to contribute.


_yatiml_recognize missing required argument
'''''''''''''''''''''''''''''''''''''''''''

If you get

.. code-block:: python

  TypeError: _yatiml_recognize() missing 1 required positional argument: 'node'

or

.. code-block:: python

  TypeError: _yatiml_savorize() missing 1 required positional argument: 'node'

then you have probably forgotten to add the ``@classmethod`` decorator to your
``_yatiml_recognize()`` or ``_yatiml_savorize()`` function.
