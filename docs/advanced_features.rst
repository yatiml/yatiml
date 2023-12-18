Advanced features
=================

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
the child class, and not consider it ambiguous. Abstract base classes (ones
inheriting from ``abc.ABC``, and/or with functions marked
``@abc.abstractmethod``) never match, as they cannot be instantiated.

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

Python's UserString class tries very hard to look like a string by overloading
various special methods. Most of the time that's fine, but sometimes you have a
class that's really not much like a string on the Python side, but still should
be written to YAML as a string. In this case, you can add :class:`yatiml.String`
as a base class. YAtiML will then expect a string on the YAML side, call
``__init__`` with that string as the sole argument, and when dumping use
``str(obj)`` to obtain the string representation to write to the YAML file
(the result is then passed to ``_yatiml_sweeten()`` if you have it, so you can
still modify it if desired). Like classes derived from ``str`` and
``UserString``, such classes can be used as keys for dictionaries, but be sure
to implement ``__hash__()`` and ``__eq__()`` to make that work on the Python
side.

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
PyYAML object. Note that this method needs to be a classmethod, since
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
only a Submission can occur. The Submission class does not have ancestors,
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

Speaking of derived classes, note that while ``_yatiml_recognize()`` is
inherited by derived classes like any other Python method, YAtiML will only use
it for the class on which it is defined; derived classes will use automatic
recognition unless they have their own ``_yatiml_recognize()``. The same goes
for ``_yatiml_savorize()`` and `` _yatiml_sweeten()``.

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
the :doc:`api`, and if you get stuck, there is the :doc:`problem_solving`
section to help you out.
