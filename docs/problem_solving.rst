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
how YAtiML processes a YAML file into Python objects.

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
``yatiml_recognize()`` method.

Incidentally, a technical term for what the recognition process does is `type
inference`, which explains the name YAtiML: it inserts type inference in the
middle of the YAML processing pipeline.

The second and third stages, savourising and type checking, only apply to custom
classes. To savourise a recognised node, YAtiML calls that node's
``yatiml_savorize()`` method, after calling those of its base classes, if any.
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

Here will hopefully be a list of all error messages that YAtiML generates, and
what may be causing them. Meanwhile, if you run into an error message you can't
figure out, please make an issue, because the solution should be here and it
isn't. Contributions are of course even more welcome! See the
:ref:`development` section for information on how to contribute.
