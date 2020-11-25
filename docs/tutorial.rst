Using YAtiML (Tutorial)
=======================

Why YAtiML?
-----------

YAML-based file formats can be very handy, as YAML is easy to write by humans,
and parsing support for it is widely available. Just read your YAML file into a
document structure (a tree of nested dicts and lists), and manipulate that in
your code.

While this works fine for simple file formats, it does not scale very well to
more complex file formats like Docker Compose-files, the Common Workflow
Language (CWL) or the Multiscale Computing Language (yMCL). Manual
error-checking is lots of work and error-prone, defaults are not set
automatically (which is especially tricky if you have multiple nested optional
objects), and the file format often ends up somewhat underspecified.

Furthermore, a small collection of nested dicts and lists may work fine, but for
more complex file formats, this becomes unwieldy and a set of objects is a
better choice. Although it is not often used this way, YAML is actually a fully
fledged object-to-text serialisation protocol. The Python yaml and ruamel.yaml
libraries will actually construct objects for you, but the class names need to
be put in the YAML file for that to work, which makes those files harder to
read and write for humans, and may be a security issue.

YAtiML is a helper library that helps address these issues. With YAtiML, you
have easy-to-read YAML for the user, and easy-to-use objects for the programmer,
with validation and automatic type recognition in between. This tutorial shows
how to use YAtiML by example. You can find the example programs shown below in
the ``docs/examples/`` directory in the repository.


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
``datetime.datetime`` and ``pathlib.Path``.

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
Python notation for type annotations. Note that YAtiML does not accept anything
other than ``str`` for the key type of a ``Dict``.

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

  yatiml.exceptions.RecognitionError:   in "<unicode string>", line 1, column 1:
      name: Janice
      ^ (line: 1)
  Type mismatch, expected a dict of string to (string)


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


Class hierarchies
-----------------

One of the main features of object oriented design is inheritance. If your
objects can be categorised in classes and subclasses, then Python lets you code
them like that, and YAtiML can read and write them.

For example, let's add a description of the drawing to our Submission, in the
form of a list of the shapes that it consists of. We'll content ourselves with
a somewhat crude representation consisting of circles and squares.

.. literalinclude:: examples/class_hierarchy.py
  :caption: ``docs/examples/class_hierarchy.py``
  :language: python

Here, we have defined a class ``Shape``, and have added a list of Shapes as an
attribute to ``Submission``. Each shape has a location, its center, which is a
list of coordinates. Classes ``Circle`` and ``Square`` inherit from
``Shape``, and have some additional attributes. All the classe are passed when
creating the load function, and that's important, because only those classes
will be considered by YAtiML.

YAtiML will automatically recognize which subclass matches the object actually
specified in the list from the attributes that it has. If more than one subclass
matches, it will give an error message stating that the file being read is
ambiguous. If both a parent class and its child class match, YAtiML will prefer
the child class, and not consider it ambiguous.

Note that the child classes include the parent's class's ``center`` attribute in
their ``__init__``, and pass it on using ``super()``. This is required, as
otherwise YAtiML won't accept the ``center`` attribute for a subclass. Another
design option here would be to automatically merge the named attributes along
the inheritance path, and allow using a ``**kwargs`` on ``__init__`` to forward
additional attributes to the parent classes. The more explicit option is more
typing, but it also makes it easier to see what's going on when reading the
code, and that's very important for code maintainability. So that's what YAtiML
does.

Enumerations
------------

Enumerations, or enums, are types that are defined by listing a set of possible
values. In Python 3, they are made by creating a class that inherits from
``enum.Enum``. YAML does not have enumerations, but strings work fine provided
that you have something like YAtiML to check that the string that the user put
in actually matches one of the values of the enum type, and return the correct
value from the enum class. Here's how to add some colour to the drawings.

.. literalinclude:: examples/enums.py
  :caption: ``docs/examples/enums.py``
  :language: python

Note that the labels that YAtiML looks for are the names of the enum members,
not their values. In many existing standards, enums map to numerical values, or
if you're making something new, it's often convenient to use the values for
something else. The names are usually what you want to write though, so they're
probably easier for the users to write in the YAML file too. If you want
something else though, you can season your enumerations. See below for a general
explanation of seasoning, or look at :ref:`seasoning_enumerations` in the
Recipes section for some examples.

User-Defined Strings
--------------------

When defining file formats, you often find yourself with a need to define a
string with constraints. For example, Dutch postal codes consist of four digits,
followed by two uppercase letters. If you use a generic string type for a postal
code, you may end up accepting invalid values. A better solution is to define a
custom string type with a built-in constraint. In Python 3, you can do this
by deriving a class either from ``str`` or from ``collections.UserString``. The
latter is easier, so that's what we'll use in this example. Let's add the town
that our participant lives in to our YAML format, but insist that it be
capitalised.

.. literalinclude:: examples/user_defined_string.py
  :caption: ``docs/examples/user_defined_string.py``
  :language: python

Python's ``UserString`` provides an attribute ``data`` containing the actual
string, so all we need to do is test that for validity in the constructor. If
you spell the town using only lowercase letters, you'll get:

.. code-block:: none

  ValueError: Invalid TitleCaseString 'piedmont': Each word must start with a
  capital letter

Note that you can't make a TitleCaseString object containing 'piedmont' from
Python either, so the object model and the YAML format are consistent.


Seasoning your YAML
-------------------

For users who are manually typing YAML files, it is usually nice to have some
flexibility. For programmers processing the data read from such a file, it is
very convenient if everything is rigidly defined, so that they do not have to
take into account all sorts of corner cases. YAtiML helps you bridge this gap
with its support for seasoning.

In programming languages, small features that make the language easier to type,
but which do not add any real functionality are known as `syntactic sugar`. With
YAtiML, you can add a bit of extra processing halfway through the dumping
process to format your object in a nicer way. YAtiML calls this `sweetening`.
When loading, you can convert back to the single representation that matches
your class definition by `savourising`, savoury being the opposite of sweet.
Together, sweetening and savourising are referred to as `seasoning`.

Let's do another example. Having ages either as strings or as ints is not very
convenient if you want to check which age category to file a submission under.
So let's add a savourising function to convert strings to int on loading:

.. literalinclude:: examples/savorizing.py
  :caption: ``docs/examples/savorizing.py``
  :language: python

We have added a new ``_yatiml_savorize()`` class method to our Submission class.
This method will be called by YAtiML after the YAML text has been parsed, but
before our Submission object has been generated. This method is passed the
`node` representing the mapping that will become the object. The node is of
type :class:`yatiml.Node`, which in turn is a wrapper for an internal
ruamel.yaml object. Note that this method needs to be a classmethod, since
there is no object yet to call it with.

The :class:`yatiml.Node` class has a number of methods that you can use to
manipulate the node. In this case, we first check if there is an ``age``
attribute at all, and if so, whether it has a string as its value. This is
needed, because we are operating on the freshly-parsed YAML input, before any
type checks have taken place. In other words, that node may contain anything.
Next, we get the attribute's value, and then try to convert it to an int and set
it as the new value. If a string value was used that we do not know how to
convert, we raise a :class:`yatiml.SeasoningError`, which is the appropriate way
to signal an error during execution of ``_yatiml_savorize()``.

(At this point I should apologise for the language mix-up; the code uses
North-American spelling because it's rare to use British spelling in code and so
it would confuse everyone, while the documentation uses British spelling because
it's what its author is used to.)

When saving a Submission, we may want to apply the opposite transformation, and
convert some ints back to strings. That can be done with a ``_yatiml_sweeten``
classmethod:

.. literalinclude:: examples/sweetening.py
  :caption: ``docs/examples/sweetening.py``
  :language: python

The ``_yatiml_sweeten()`` method has the same signature as
``_yatiml_savorize()`` but is called when dumping rather than when loading. It
gives you access to the YAML node that has been produced from a Submission
object before it is written out to the YAML output. Here, we use the same
functions as before to convert some of the int values back to strings. Since we
converted all the strings to ints on loading above, we can assume that the value
is indeed an int, and we do not have to check.

Indeed, if we run this example, we get:

.. code-block:: none

  name: Youssou
  age: seven
  tool: pencils

However, there is still an issue. We have now used the seasoning functionality
of YAtiML to give the user the freedom to write ages either as words or as
numbers, while always giving the programmer ints to work with. However, the
programmer could still accidentally put a string into the age field when
constructing a Submission directly in the code, as the type annotation allows
it. This would then crash the ``_yatiml_sweeten()`` method when trying to dump
the object.

The solution, of course, is to change the type on the ``age`` attribute of
``__init__`` to ``int``. Unfortunately, this breaks loading. If you try to run
the savourise example above with ``age`` as type ``int``, then you will get

.. code-block:: none

  yatiml.exceptions.RecognitionError:   in "<unicode string>", line 1, column 1:
      name: Janice
      ^ (line: 1)
  Type mismatch, expected a Submission

The reason we get the error above is that by default, YAtiML recognises objects
of custom classes by their attributes, checking both names and types.
With the type of the ``age`` attribute now defined as ``int``, a mapping
containing an ``age`` with a string value is now no longer recognised as a
Submission object. A potential solution would be to apply seasoning before
trying to recognise, but to know how to savorise a mapping we need to know which
type it is or should be, and for that we need to recognise it. The way to fix
this is to override the default recognition function with our own, and make that
recognise both ``int`` and ``str`` values for ``age``.

Customising recognition
-----------------------

Customising the recognition function is done by adding a
``_yatiml_recognize()`` method to your class, like this:

.. literalinclude:: examples/custom_recognition.py
  :caption: ``docs/examples/custom_recognition.py``
  :language: python

This is again a classmethod, with a single argument of type
:class:`yatiml.UnknownNode` representing the node. Like
:class:`yatiml.Node`, :class:`yatiml.UnknownNode` wraps a YAML node, but this
class has helper functions intended for writing recognition functions.  Here,
we use :meth:`require_attribute` to list the required attributes and their
types. Since ``tool`` is optional, it is not required, and not listed. The
``age`` attribute is specified with the Union type we used before. Now, any
mapping that is in a place where we expect a Submission will be recognised as a
Submission, as long as it has a ``name`` attribute with a string value, and an
``age`` attribute that is either a string or an integer. If ``age`` is a
string, the ``_yatiml_savorize()`` method will convert it to an int, after
which a Submission object can be constructed without violating the type
constraint in the ``__init__()`` method.

In fact, the ``_yatiml_recognize()`` method here could be even simpler. In
every place in our document where a Submission can occur (namely the root),
only a Submission can occur. The Submission class does not have descendants,
and it is never part of a Union. So there is never any doubt as to how to treat
the mapping, and in fact, the following will also work:

.. code-block:: python

  @classmethod
  def _yatiml_recognize(cls, node: yatiml.UnknownNode) -> None:
      pass

Now, if you try to read a document with, say, a float argument to ``age``, it
will be recognised as a Submission, the ``_yatiml_savorize()`` method will do
nothing with it, and you'll get an error message at the type check just before a
Submission is constructed.

This makes it clear that recognition is not a type check. Instead, its job is to
distinguish between different possible types in places where the class hierarchy
leaves some leeway to put in objects of different classes. If there is no such
leeway, the recognition stage does not need to do anything. If there is some
leeway, it just needs to do the minimum to exclude other possibilities.

However, since data models tend to evolve, it is usually a good idea to do a
full check anyway, so that if this class ends up being used in a Union, or if
you or someone else adds derived classes later, things will still work correctly
and there won't be any unnecessary ambiguity errors for the users.

Extra attributes
----------------

By default, YAtiML will match a mapping in a YAML file exactly: each required
attribute must be there, and any extraneous attributes give an error. However,
you may want to give your users the option of adding additional attributes. The
logical way for YAtiML to support this would be through having a ``**kwargs``
attribute to the ``__init__`` method, but unfortunately this would lose the
ordering information, since ``**kwargs`` is a plain unordered dict (although
this is in the process of changing in newer versions of Python). Also, there
wouldn't be an obvious way of saving such extra attributes again.

So, instead, extra attributes are sent to a ``_yatiml_extra`` parameter of type
``OrderedDict`` on ``__init__``, if there is one. You put this value into a
``_yatiml_extra`` attribute, whose contents YAtiML will then dump appended to
the normal attributes. If you want to be able to add extra attributes when
constructing an object using keyword arguments, then you can add a ``**kwargs``
parameter as well, and put any key-value pairs in it into ``self._yatiml_extra``
in your favourite order yourself.

Here is an example:

.. literalinclude:: examples/extra_attributes.py
  :caption: ``docs/examples/extra_attributes.py``
  :language: python

In this example, we use the ``tool`` attribute again, but with this code, we
could add any attribute, and it would show up in ``_yatiml_extra`` with no
errors generated.

Note that any explicit YAML tags on any mapping values of the extra attributes
or anywhere beneath them in the YAML tree will be stripped, so that this tree
will consist of plain lists and dicts. This is to avoid unexpected
user-controlled object construction, for safety reasons. These tags are
currently not added back on saving either, so it's good if the extra data does
not rely on them, better if it does not have any.

.. _hiding-attributes:

Hiding attributes
-----------------

By default, YAtiML assumes that your classes have a public attribute
corresponding to each parameter of their ``__init__`` method. If this
arrangement does not work for you, then you can override it by creating a
``_yatiml_attributes()`` method. This is `not` a classmethod, but an ordinary
method, because it is used for saving a particular instance of your class, to
which it needs access. If your custom class has a ``_yatiml_attributes()``
method defined, YAtiML will call that method instead of looking for public
attributes.  It should return an ``OrderedDict`` with names and values of the
attributes.

So far, we have been printing the values of public attributes to see the results
of our work. It would be better encapsulation to use private attributes instead,
with a ``__str__`` method to help printing. With ``_yatiml_attributes()``, that
can be done:

.. literalinclude:: examples/private_attributes.py
  :caption: ``docs/examples/private_attributes.py``
  :language: python

Further reading
---------------

You've reached the end of this tutorial, which means that you have seen all the
major features that YAtiML has. If you haven't already started, now is the time
to start making your awn YAML-based file format. You may want to have a look at
the :doc:`API documentation<apidocs/yatiml>`, and if you get stuck, there is the
:doc:`problem_solving` section to help you out.
