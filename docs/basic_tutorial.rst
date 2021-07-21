Basic Tutorial
==============

With YAtiML, you have easy-to-read YAML for the user, and easy-to-use objects
for the programmer, with validation and automatic type recognition in between.
This tutorial shows how to use YAtiML by example. You can find the example
programs shown below in the ``docs/examples/`` directory in the repository.

A first example
---------------

For a first example, we will pass on object conversion and just read a simple
dictionary (or in YAML terms, a mapping). Let's say that we're organising a
drawing contest for kids, and are tracking submissions in YAML files.

For the example to run, make sure that you have :ref:`installed YAtiML
<installing>` first.

.. literalinclude:: examples/dict_of_strings.py
  :caption: ``docs/examples/dict_of_strings.py``
  :language: python

If you run this program, it will output

.. code-block:: none

  ordereddict([('name', 'Janice'), ('age', 'Six')])


There is quite a bit going on in this example, so let's take it one bit at a
time.

.. code-block:: python

  from typing import Dict


To tell YAtiML which type of objects it should construct, and therefore which
kind of document it should expect, we use the built-in Python types, and the
definitions from the standard ``typing`` module. If you use type annotations in
your Python code, then you will already be familiar with them. If not, you will
find plenty of examples in this tutorial.

For reference, YAtiML supports these built-in and standard types: ``str``,
``int``, ``float``, ``bool``, ``typing.Dict``, ``typing.List``,
``typing.Mapping``, ``typing.Sequence``, ``typing.Union``,
``datetime.date`` and ``pathlib.Path``.

.. code-block:: python

  import yatiml


Here is where we import the YAtiML library itself.

.. code-block:: python

  load = yatiml.load_function(Dict[str, str])

This is where we first start using YAtiML. To load a YAML file, we need a
function that can do so. This call makes a function (!) called ``load`` which
can load and check YAML files containing a dictionary with strings as keys and
also strings as values. The ``Dict`` type (rather than a plain ``dict``, which
won't let us specify the key and value types) and square brackets are standard
Python notation for type annotations. Note that YAtiML only accepts strings for
the key type of a ``Dict``, either ``str`` or a user defined one (see below).

.. code-block:: python

  doc = load(yaml_text)


Here, we load the YAML document using our newly created function. Other than a
string, you can also open a stream object (an opened file) or a ``pathlib.Path``
object pointing to a file.

.. code-block:: none

  ordereddict([('name', 'Janice'), ('age', 'Six')])


One immediately visible difference is in the result: it is not a plain Python
``dict``, but an ``OrderedDict``. This is a standard Python type from the
``collections`` module that works just like a normal ``dict``, but remembers the
order of the entries.  Saving a ``dict`` to a YAML file using plain PyYAML will
put the attributes in a random order, which is usually difficult to read.
YAtiML keeps the order of the attributes, so you can make your YAML file more
readable.

Type errors
-----------

So far, we have defined the type of our document, and read a matching YAML file.
But what if we are given a YAML file that does not match? Let's modify our input
a bit, writing the age as a number:

.. literalinclude:: examples/type_error.py
  :caption: ``docs/examples/type_error.py``
  :language: python

Running this modified version gives an exception traceback ending with:

.. code-block:: none

  yatiml.exceptions.RecognitionError: Failed to recognize a string
    in "<unicode string>", line 2, column 6:
      age: 6
           ^ (line: 2)


What has happened here is that YAML has recognised ``6`` as an ``int``. Since it
is a value in the dictionary, YAtiML then compared that ``int`` type to the
second argument of ``Dict``, which is ``str``, found a mismatch, and gave an
error message.

In particular, it raised a ``yatiml.RecognitionError``. In general,
if your input document does not match the type you specified, this exception
will be raised, with an error message pointing to the point in the YAML file
where the problem was found.

One way to solve this problem is to tell YAtiML to accept both ints and strings
as values in the dictionary. We can do this using a ``Union`` type:

.. literalinclude:: examples/union_dict.py
  :caption: ``docs/examples/union_dict.py``
  :language: python

However, this will also make YAtiML accept an ``int`` for the ``name``
attribute, which may not be what we want. In order to improve on this, we'll
have to abandon the use of a dict, and define a custom class.

Custom classes
--------------

Custom classes in YAtiML are actually quite ordinary Python classes. They have
an ``__init__`` method, which is very important to YAtiML, and may have some
other special methods that interact with YAtiML. Here's our example again, but
now using a custom class:

.. literalinclude:: examples/custom_class.py
  :caption: ``docs/examples/custom_class.py``
  :language: python

We have added a new class ``Submission``, which represents a submission for our
drawing contest. It has an ``__init__`` method with two arguments (and ``self``,
of course). While this is an ordinary Python ``__init__`` method, for YAtiML
there are two special things about it: the order of the parameters, and the type
annotations.

The order of the parameters is used by YAtiML when saving an object of this
class to YAML, they'll be saved in this order. So you should make sure that the
order makes sense, because that is what people will see. Note that it is the
order of the parameters of the ``__init__`` method that matters, not the order
in which the arguments are assigned to the attributes in the body of that
method.

The type annotations on the ``__init__`` method are used by YAtiML to check that
the YAML document it is reading is in the correct form. For a custom class like
this, it will expect to see a mapping (dict) with keys ``name`` and ``age``,
with a string value for ``name``, and either an int or a string for ``age``. If
it finds this, it will create a ``Submission`` object, passing the values from
the YAML document to the constructor.

In this example, the attributes themselves do not have a type annotation. You
are free to add some, but YAtiML will not use them. For YAtiML, the types of the
attributes are determined by the annotations on the ``__init__`` method only.

Sometimes, you want to add further constraints on the attributes of the class.
For example, maybe our contestants' ``age`` may be at most ``12``. The standard
thing to do in this situation is to add a check to ``__init__``, and raise a
``ValueError`` if it fails. If that happens during loading, then YAtiML will
output the associated message and point out where in the input the problem is.

Note that the loader is now passed our custom class, rather than a ``Dict``:

.. code-block:: python

  load = yatiml.load_function(Submission)

For more complex file formats, you will likely have a custom class that
describes the document, which has attributes that themselves are of a custom
class type. In this case, all these custom class types need to be added to the
arguments, with the one that describes the whole document first.

This new example outputs the following:

.. code-block:: none

  <class '__main__.Submission'>
  Janice
  6
  <class 'int'>

Note that the main document has been recognised as a ``Submission``, and an
object of this class was returned. Attribute ``age`` is of type ``int``, because
that is what was actually in the YAML file. While the definition of an attribute
may allow for objects of multiple types (using a ``Union``, or when specifying a
base class that has multiple subclasses), in the object you get from reading a
YAML file, each attribute has one specific type.

Note that on Python 3.7 or later, you can also use
`dataclasses <https://docs.python.org/3/library/dataclasses.html>`_, like this:

.. literalinclude:: examples/data_classes.py
  :caption: ``docs/examples/data_classes.py``
  :language: python

However, since you're not writing the ``__init__`` function yourself, checks for
valid values like above are not possible in this case, so if you want those
you'll have to do it with a normal class.


Default values
--------------

One of the issues you will run into when implementing a complex YAML-based
format by hand, is default values. For example in a configuration file, it is
often much easier if the users can completely omit any options for which a
default value suffices. If you have nested optional structures (e.g. users are
allowed to omit an entire dictionary if its attributes have all been omitted),
then processing the data becomes a tedious set of nested ifs. In YAtiML,
default values are easy: since ``__init__`` parameters map to attributes, all
you have to do is declare a parameter with a default value:

.. literalinclude:: examples/default_values.py
  :caption: ``docs/examples/default_values.py``
  :language: python

Here we have added the tool that was used as an argument with a default value.
If the YAML file contains a key ``tool`` with a string value, that value will be
passed to the ``__init__`` method. If the key ``tool`` exists, but the value is
not of type string, a ``RecognitionError`` is raised. If the key is missing, the
default value is used.

Note that in this case, the ``tool`` attribute is optional in the YAML file, but
not in the class: every object of type ``Submission`` has to have a value for
``tool`` that is not ``None``. This allows you to conveniently skip the check,
which gets rid of those nested ifs if you have nested optional entries in your
YAML file.

However, you may want to make the attribute optional in the class as well, and
perhaps set ``None`` as the default value. That is done like this:

.. literalinclude:: examples/optional_attribute.py
  :caption: ``docs/examples/optional_attribute.py``
  :language: python

Now the value of a ``Submission`` object's ``tool`` attribute can be ``None``,
and it will be if that attribute is omitted in the YAML mapping. Note that this
definition is entirely standard Python 3, there is nothing YAtiML-specific in
it.

Saving to YAML
--------------

There is more to be said about loading YAML files with YAtiML, but let's first
have a look at saving objects back to YAML, or dumping as PyYAML and ruamel.yaml
call it. The code for this is a mirror image of the loading code:

.. literalinclude:: examples/saving.py
  :caption: ``docs/examples/saving.py``
  :language: python

And as expected, it outputs:

.. code-block:: none

  name: Youssou
  age: 7
  tool: pencils

YAtiML expects a public attribute with the same name for each parameter in the
``__init__`` method to exist, and will use its value in saving. This can be
overridden, see :ref:`hiding-attributes` below.

Note that the attributes are in the order of the parameters of the ``__init__``
method. YAtiML always outputs attributes in this order, even if the object was
read in with YAtiML from a YAML file and originally had a different order. While
it would be nice to do full round-trip formatting of the input YAML, support for
this in the ruamel.yaml library used by YAtiML is still developing, so for now
this is what YAtiML does.

:meth:`yatiml.dumps_function` creates a function that converts objects to a
string. If you want to write the output to a file directly, you can use
:meth:`yatiml.dump_function` instead to create a function that can do that.

As an example of the advantage of using YAtiML, saving a Submission document
with PyYAML or ruamel.yaml gives this:

.. code-block:: none

  !!python/object:__main__.Submission {age: 7, name: Youssou, tool: pencils}

which is not nearly as nice to read or write. (To be fair, ruamel.yaml can do a
bit nicer than this with its RoundTripDumper, which YAtiML uses, but the tag
with the exclamation marks remains.)

Saving to JSON
--------------

YAML is a superset of JSON, so YAtiML can read JSON files. If you want to save
JSON as well, then you can use :meth:`yatiml.dumps_json_function` instead:

.. code-block:: python

  # Create dumper
  dumps = yatiml.dumps_json_function(Submission)
