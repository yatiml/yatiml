Using YAtiML (Tutorial)
=======================

Why YAtiML?
-----------

YAML-based file formats can be very handy, as YAML is easy to write by humans,
and parsing support for it is widely available. Just read your YAML file into a
document structure (a tree of nested dicts and lists), and manipulate that in
your code.

While this works fine for simple file formats, it does not scale very well to
more complex file formats such as the Common Workflow Language (CWL) or the
Multiscale Computing Language (yMCL). Manual error-checking is lots of work and
error-prone, defaults are not set automatically (which is especially tricky if
you have multiple nested optional objects), and the file format often ends up
somewhat underspecified.

Furthermore, a small collection of nested dicts and lists may work fine, but for
more complex file formats, this becomes unwieldy and a set of objects is a
better choice. Although it is not often used this way, YAML is actually a fully
fledged object-to-text serialisation protocol. The Python yaml and ruamel.yaml
libraries will actually construct objects for you, but the class names need to
be put in the YAML file for that to work, which makes those files harder to
read and write for humans.

YAtiML is a helper library that helps address these issues. With YAtiML, you
have easy-to-read YAML for the user, and easy-to-use objects for the programmer,
with validation and automatic type recognition in between. This tutorial shows
how to use YAtiML by example. You can find the example programs shown below in
the ``examples/`` directory in the repository.


A first example
---------------

For a first example, we will pass on object conversion and just read a simple
dictionary (or in YAML terms, a mapping). Let's say that we're organising a
drawing contest for kids, and are tracking submissions in YAML files.

For the example to run, make sure that you have :ref:`installed YAtiML
<installing>` first.

.. code-block:: python
  :caption: ``dict_of_strings.py``

  from ruamel import yaml
  from typing import Dict
  import yatiml


  # Create loader
  class MyLoader(yatiml.Loader):
      pass

  yatiml.set_document_type(MyLoader, Dict[str, str])

  # Load YAML
  yaml_text = ('name: Janice\n'
               'age: Six\n')
  doc = yaml.load(yaml_text, Loader=MyLoader)
  print(doc)


If you run this program, it will output

.. code-block:: none

  ordereddict([('name', 'Janice'), ('age', 'Six')])


There is quite a bit going on in this example, so let's take it one bit at a
time.

.. code-block:: python

  from ruamel import yaml


YAtiML is built upon ruamel.yaml, a fork of PyYAML. We chose ruamel.yaml because
it is more actively maintained, and has some support for comments and formatting
of YAML files, which is important for making the files easier to work with
directly by users. When you install YAtiML, ruamel.yaml is automatically
installed as well.

.. code-block:: python

  from typing import Dict


To tell YAtiML which type of objects it should construct, and therefore which
kind of document it should expect, we use the built-in Python types, and the
definitions from the standard ``typing`` module. If you use type annotations in
your Python code, then you will already be familiar with them. If not, you will
find plenty of examples in this tutorial.

.. code-block:: python

  import yatiml


Here is where we import the YAtiML library itself.

.. code-block:: python

  class MyLoader(yatiml.Loader):
      pass


This is where we first start using YAtiML. To read YAML files, ruamel.yaml uses
a Loader. It has several built-in loaders, but since we want to do some special
things during the loading process, we specify our own loader class. Since the
special things are all done for you by YAtiML, the class itself can be empty,
but it must inherit from ``yatiml.Loader`` for YAtiML to be able to do its work.

.. code-block:: python

  yatiml.set_document_type(MyLoader, Dict[str, str])


The one remaining thing to do before we can load some YAML data is to tell our
Loader which kind of object it should create from the YAML file. Here, we tell
it to create a dictionary, with strings as keys and also strings as values. The
``Dict`` type (rather than a plain ``dict``, which won't let us specify the key
and value types) and square brackets are standard Python notation for type
annotations. Note that YAtiML does not accept anything other than ``str`` for
the key type of a ``Dict``.

Creating a class first and then calling a separate function to modify it is a
bit odd. It would be nicer if we could just construct a Loader object and pass
the document type to its constructor. However, due to the design of ruamel.yaml
(which it inherited from PyYAML), implementing this turned out to cause a lot of
trouble, so we decided to do it the PyYAML way.


.. code-block:: python

  doc = yaml.load(yaml_text, Loader=MyLoader)


Here, we load the YAML document. Note that we're using the standard ``load()``
function from ruamel.yaml, as you normally would. The only difference is that
the new MyLoader class is passed to the function, causing it to work differently
than it normally would have.

.. code-block:: none

  ordereddict([('name', 'Janice'), ('age', 'Six')])


One immediately visible difference is in the result: it is not a plain Python
``dict``, but an ``OrderedDict``. This is a standard Python type from the
``collections`` module that works just like a normal ``dict``, but remembers the
order of the entries.  Saving a ``dict`` to a YAML file using plain PyYAML will
put the attributes in a random order, which is usually difficult to read. With
ruamel.yaml, YAtiML can control the order, and it makes use of that feature
here.

Type errors
-----------

So far, we have define the type of our document, and read a matching YAML file.
But what if we are given a YAML file that does not match? Let's modify our input
a bit, writing the age as a number:

.. code-block:: python
  :caption: ``type_error.py``

  from ruamel import yaml
  from typing import Dict
  import yatiml


  # Create loader
  class MyLoader(yatiml.Loader):
      pass

  yatiml.set_document_type(MyLoader, Dict[str, str])

  # Load YAML
  yaml_text = ('name: Janice\n'
               'age: 6\n')
  doc = yaml.load(yaml_text, Loader=MyLoader)
  print(doc)


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

.. code-block:: python
  :caption: ``union_dict.py``

  from ruamel import yaml
  from typing import Dict, Union
  import yatiml


  # Create loader
  class MyLoader(yatiml.Loader):
      pass

  yatiml.set_document_type(MyLoader, Dict[str, Union[str, int]])

  # Load YAML
  yaml_text = ('name: Janice\n'
               'age: 6\n')
  doc = yaml.load(yaml_text, Loader=MyLoader)
  print(doc)

However, this will also make YAtiML accept an ``int`` for the ``name``
attribute, which may not be what we want. In order to improve on this, we'll
have to abandon the use of a dict, and define a custom class.

Custom classes
--------------

Custom classes in YAtiML are actually quite ordinary Python classes. They have
an ``__init__`` method, which is very important to YAtiML, and may have some
other special methods that interact with YAtiML. Here's our example again, but
now using a custom class:

.. code-block:: python
  :caption: ``custom_class.py``

  from ruamel import yaml
  from typing import Union
  import yatiml


  # Create document class
  class Submission:
      def __init__(self, name: str, age: Union[int, str]) -> None:
          self.name = name
          self.age = age

  # Create loader
  class MyLoader(yatiml.Loader):
      pass

  yatiml.add_to_loader(MyLoader, Submission)
  yatiml.set_document_type(MyLoader, Submission)

  # Load YAML
  yaml_text = ('name: Janice\n'
               'age: 6\n')
  doc = yaml.load(yaml_text, Loader=MyLoader)

  print(type(doc))
  print(doc.name)
  print(doc.age)
  print(type(doc.age))

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
it finds this, it will instruct ruamel.yaml to create a ``Submission`` object,
passing the values from the YAML document to the constructor.

In this example, the attributes themselves do not have a type annotation. You
are free to add some, but YAtiML will not use them. For YAtiML, the types of the
attributes are determined by the annotations on the ``__init__`` method only.

There is another new line in the script:

.. code-block:: python

  yatiml.add_to_loader(MyLoader, Submission)

This registers the new custom class with ``MyLoader``, which will allow it to
construct ``Submission`` objects. Note that you still have to set the document
type as well. For more complex file formats, you will likely have a custom class
that describes the document, which has attributes that themselves are of a
custom class type. In this case, all these custom class types need to be added
to the loader, but only the one that describes the whole document is set as the
document type.

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

.. code-block:: python
  :caption: ``default_values.py``

  from ruamel import yaml
  from typing import Union
  import yatiml


  # Create document class
  class Submission:
      def __init__(
              self,
              name: str,
              age: Union[int, str],
              tool: str='crayons'
              ) -> None:
          self.name = name
          self.age = age
          self.tool = tool


  # Create loader
  class MyLoader(yatiml.Loader):
      pass

  yatiml.add_to_loader(MyLoader, Submission)
  yatiml.set_document_type(MyLoader, Submission)

  # Load YAML
  yaml_text = ('name: Janice\n'
               'age: 6\n')
  doc = yaml.load(yaml_text, Loader=MyLoader)

  print(doc.name)
  print(doc.age)
  print(doc.tool)


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

.. code-block:: python
  :caption: ``optional_attribute.py``

  from ruamel import yaml
  from typing import Optional, Union
  import yatiml


  # Create document class
  class Submission:
      def __init__(
              self,
              name: str,
              age: Union[int, str],
              tool: Optional[str]=None
              ) -> None:
          self.name = name
          self.age = age
          self.tool = tool

  # Identical remainder omitted

Now the value of a ``Submission`` object's ``tool`` attribute can be ``None``,
and it will be if that attribute is omitted in the YAML mapping. Note that this
definition is entirely standard Python 3, there is nothing YAtiML-specific in
it.

Saving to YAML
--------------

There is more to be said about loading YAML files with YAtiML, but let's first
have a look at saving objects back to YAML, or dumping as PyYAML and ruamel.yaml
call it. The code for this is a mirror image of the loading code:

.. code-block:: python
  :caption: ``saving.py``

  from ruamel import yaml
  from typing import Optional, Union
  import yatiml


  # Create document class
  class Submission:
      def __init__(
              self,
              name: str,
              age: Union[int, str],
              tool: Optional[str]=None
              ) -> None:
          self.name = name
          self.age = age
          self.tool = tool


  # Create dumper
  class MyDumper(yatiml.Dumper):
      pass

  yatiml.add_to_dumper(MyDumper, Submission)


  # Dump YAML
  doc = Submission('Youssou', 7, 'pencils')
  yaml_text = yaml.dump(doc, Dumper=MyDumper)

  print(yaml_text)

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
this in ruamel.yaml is still developing, so for now this is what YAtiML does.

As an example of the advantage of using YAtiML, try using the default ``Dumper``
instead of the custom YAtiML one:

.. code-block:: python

  yaml_text = yaml.dump(doc)

This will give

.. code-block:: none

  !!python/object:__main__.Submission {age: 7, name: Youssou, tool: pencils}

which is not nearly as nice to read or write. (To be fair, ruamel.yaml can do a
bit nicer than this with its RoundTripDumper, which YAtiML uses, but the tag
with the exclamation marks remains.)

Class hierarchies
-----------------

One of the main features of object oriented design is inheritance. If your
objects can be categorised in classes and subclasses, then Python lets you code
them like that, and YAtiML can read and write them.

For example, let's add a description of the drawing to our Submission, in the
form of a list of the shapes that it consists of. We'll content ourselves with
a somewhat crude representation consisting of circles and squares.

.. code-block:: python
  :caption: class_hierarchy.py

  from ruamel import yaml
  from typing import List, Union
  import yatiml


  # Create document classes
  class Shape:
      def __init__(self, center: List[float]) -> None:
          self.center = center


  class Circle(Shape):
      def __init__(self, center: List[float], radius: float) -> None:
          super().__init__(center)
          self.radius = radius


  class Square(Shape):
      def __init__(self, center: List[float], width: float, height: float) -> None:
          super().__init__(center)
          self.width = width
          self.height = height


  class Submission(Shape):
      def __init__(
              self,
              name: str,
              age: Union[int, str],
              drawing: List[Shape]
              ) -> None:
          self.name = name
          self.age = age
          self.drawing = drawing


  # Create loader
  class MyLoader(yatiml.Loader):
    pass

  yatiml.add_to_loader(MyLoader, [Shape, Circle, Square, Submission])
  yatiml.set_document_type(MyLoader, Submission)

  # Load YAML
  yaml_text = ('name: Janice\n'
               'age: 6\n'
               'drawing:\n'
               '  - center: [1.0, 1.0]\n'
               '    radius: 2.0\n'
               '  - center: [5.0, 5.0]\n'
               '    width: 1.0\n'
               '    height: 1.0\n')
  doc = yaml.load(yaml_text, Loader=MyLoader)

  print(doc.name)
  print(doc.age)
  print(doc.drawing)

Here, we have defined a class ``Shape``, and have added a list of Shapes as an
attribute to ``Submission``. Each shape has a location, its center, which is a
list of coordinates. Classes ``Circle`` and ``Square`` inherit from
``Shape``, and have some additional attributes. All the classe are added to the
Loader, and that's important, because only classes added to the Loader will be
considered by YAtiML.

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

.. code-block:: python
  :caption: ``savorizing.py``

  from ruamel import yaml
  from typing import Optional, Union
  import yatiml


  # Create document class
  class Submission:
      def __init__(
              self,
              name: str,
              age: Union[int, str],
              tool: Optional[str]=None
              ) -> None:
          self.name = name
          self.age = age
          self.tool = tool

      @classmethod
      def yatiml_savorize(cls, node: yatiml.ClassNode) -> None:
          str_to_int = {
                  'five': 5,
                  'six': 6,
                  'seven': 7,
                  }
          if node.has_attribute_type('age', str):
              str_val = node.get_attribute('age').value
              if str_val in str_to_int:
                  node.set_attribute('age', str_to_int[str_val])
              else:
                  raise yatiml.SeasoningError('Invalid age string')


  # Create loader
  class MyLoader(yatiml.Loader):
      pass

  yatiml.add_to_loader(MyLoader, Submission)
  yatiml.set_document_type(MyLoader, Submission)

  # Load YAML
  yaml_text = ('name: Janice\n'
               'age: six\n')
  doc = yaml.load(yaml_text, Loader=MyLoader)

  print(doc.name)
  print(doc.age)
  print(doc.tool)


We have added a new ``yatiml_savorize()`` class method to our Submission class.
This method will be called by YAtiML after the YAML text has been parsed, but
before our Submission object has been generated. This method is passed the
`node` representing the mapping that will become the object. The node is of type
``yatiml.ClassNode``, which in turn is a wrapper for an internal ruamel.yaml
object. Note that this method needs to be a classmethod, since there is no
object yet to call it with.

The :class:`yatiml.ClassNode` class has a number of methods that you can use to
manipulate the node. In this case, we first check if there is an ``age``
attribute at all, and if so, whether it has a string as its value. This is
needed, because we are operating on the freshly-parsed YAML input, before any
type checks have taken place. In other words, that node may contain anything.
Next, we get the attribute's value, and then try to convert it to an int and set
it as the new value. If a string value was used that we do not know how to
convert, we raise a :class:`yatiml.SeasoningError`, which is the appropriate way
to signal an error during execution of ``yatiml_savorize()``.

(At this point I should apologise for the language mix-up; the code uses
North-American spelling because it's rare to use British spelling in code and so
it would confuse everyone, while the documentation uses British spelling because
it's what its author is used to.)

When saving a Submission, we may want to apply the opposite transformation, and
convert some ints back to strings. That can be done with a ``yatiml_sweeten``
classmethod:

.. code-block:: python
  :caption: ``sweetening.py``

  from ruamel import yaml
  from typing import Optional, Union
  import yatiml


  # Create document class
  class Submission:
      def __init__(
              self,
              name: str,
              age: Union[int, str],
              tool: Optional[str]=None
              ) -> None:
          self.name = name
          self.age = age
          self.tool = tool

      @classmethod
      def yatiml_sweeten(cls, node: yatiml.ClassNode) -> None:
          int_to_str = {
                  5: 'five',
                  6: 'six',
                  7: 'seven'
                  }
          int_val = int(node.get_attribute('age').value)
          if int_val in int_to_str:
              node.set_attribute('age', int_to_str[int_val])


  # Create dumper
  class MyDumper(yatiml.Dumper):
      pass

  yatiml.add_to_dumper(MyDumper, Submission)


  # Dump YAML
  doc = Submission('Youssou', 7, 'pencils')
  yaml_text = yaml.dump(doc, Dumper=MyDumper)

  print(yaml_text)

The ``yatiml_sweeten()`` method has the same signature as ``yatiml_savorize()``,
but is called by a Dumper, not by a Loader. It gives you access to the YAML node
that has been produced from a Submission object before it is written out to the
YAML output. Here, we use the same functions as before to convert some of the
int values back to strings. Since we converted all the strings to ints on
loading above, we can assume that the value is indeed an int, and we do not have
to check.

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
it. This would then crash the ``yatiml_sweeten()`` method when trying to dump
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

Customising the recognition function is done by adding a ``yatiml_recognize()``
method to your class, like this:

.. code-block:: python
  :caption: ``custom_recognition.py``

  # Initial identical lines omitted

  class Submission:
      def __init__(
              self,
              name: str,
              age: int,
              tool: Optional[str]=None
              ) -> None:
          self.name = name
          self.age = age
          self.tool = tool

      @classmethod
      def yatiml_recognize(cls, node: yatiml.UnknownNode) -> None:
          node.require_attribute('name', str)
          node.require_attribute('age', Union[int, str])

      @classmethod
      def yatiml_savorize(cls, node: yatiml.ClassNode) -> None:
          str_to_int = {
                  'five': 5,
                  'six': 6,
                  'seven': 7,
                  }
          if node.has_attribute_type('age', str):
              str_val = node.get_attribute('age').value
              if str_val in str_to_int:
                  node.set_attribute('age', str_to_int[str_val])
              else:
                  raise yatiml.SeasoningError('Invalid age string')

  # Remaining identical lines omitted

This is again a classmethod, with a single argument of type
:class:``yatiml.UnknownNode`` representing the node. Like
:class:``yatiml.ClassNode``, :class:``yatiml.UnknownNode`` wraps a YAML node,
but this class has helper functions intended for writing recognition functions.
Here, we use ``require_attribute()`` to list the required attributes and their
types. Since ``tool`` is optional, it is not required, and not listed. The
``age`` attribute is specified with the Union type we used before. Now, any
mapping that is in a place where we expect a Submission will be recognised as a
Submission, as long as it has a ``name`` attribute with a string value, and an ``age``
attribute that is either a string or an integer. If ``age`` is a string, the
``yatiml_savorize()`` method will convert it to an int, after which a Submission
object can be constructed without violating the type constraint in the
``__init__()`` method.

In fact, the ``yatiml_recognize()`` method here could be even simpler. In every
place in our document where a Submission can occur (namely the root), only a
Submission can occur. The Submission class does not have descendants, and it is
never part of a Union. So there is never any doubt as to how to treat the
mapping, and in fact, the following will also work:

.. code-block:: python

  @classmethod
  def yatiml_recognize(cls, node: yatiml.UnknownNode) -> None:
      pass

Now, if you try to read a document with, say, a float argument to ``age``, it
will be recognised as a Submission, the ``yatiml_savorize()`` method will do
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

So, instead, extra attributes are sent to a ``yatiml_extra`` parameter of type
``OrderedDict`` on ``__init__``, if there is one. You put this value into a
``yatiml_extra`` public attribute, whose contents YAtiML will then dump appended
to the normal attributes. If you want to be able to add extra attributes when
constructing an object using keyword arguments, then you can add a ``**kwargs``
parameter as well, and put any key-value pairs in it into ``self.yatiml_extra``
in your favourite order yourself.

Here is an example:

.. code-block:: python
  :caption: ``extra_attributes.py``

  from ruamel import yaml
  from collections import OrderedDict
  from typing import Union
  import yatiml


  # Create document class
  class Submission:
      def __init__(
              self,
              name: str,
              age: int,
              yatiml_extra: OrderedDict
              ) -> None:
          self.name = name
          self.age = age
          self.yatiml_extra = yatiml_extra


  # Create loader
  class MyLoader(yatiml.Loader):
      pass

  yatiml.add_to_loader(MyLoader, Submission)
  yatiml.set_document_type(MyLoader, Submission)

  # Load YAML
  yaml_text = ('name: Janice\n'
               'age: 6\n'
               'tool: crayons\n')
  doc = yaml.load(yaml_text, Loader=MyLoader)

  print(doc.name)
  print(doc.age)
  print(doc.yatiml_extra['tool'])

In this example, we use the ``tool`` attribute again, but with this code, we
could add any attribute, and it would show up in ``yatiml_extra`` with no errors
generated.

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
``yatiml_attributes()`` method. This is `not` a classmethod, but an ordinary
method, because it is used for saving a particular instance of your class, to
which it needs access. If your custom class has a ``yatiml_attributes()`` method
defined, YAtiML will call that method instead of looking for public attributes.
It should return an ``OrderedDict`` with names and values of the attributes.

So far, we have been printing the values of public attributes to see the results
of our work. It would be better encapsulation to use private attributes instead,
with a ``__str__`` method to help printing. With ``yatiml_attributes()``, that
can be done:

.. code-block:: python
  :caption: ``private_attributes.py``

  from ruamel import yaml
  from collections import OrderedDict
  from typing import Union
  import yatiml


  # Create document class
  class Submission:
      def __init__(self, name: str, age: Union[int, str]) -> None:
          self.__name = name
          self.__age = age

      def __str__(self) -> str:
          return '{}\n{}'.format(self.__name, self.__age)

      def yatiml_attributes(self) -> OrderedDict:
          return OrderedDict([
              ('name', self.__name),
              ('age', self.__age)])


  # Create loader
  class MyLoader(yatiml.Loader):
    pass

  yatiml.add_to_loader(MyLoader, Submission)
  yatiml.set_document_type(MyLoader, Submission)

  # Load YAML
  yaml_text = ('name: Janice\n'
               'age: 6\n')
  doc = yaml.load(yaml_text, Loader=MyLoader)
  print(doc)

Further reading
---------------

You've reached the end of this tutorial, which means that you have seen all the
major features that YAtiML has. If you haven't already started, now is the time
to start making your awn YAML-based file format. You may want to have a look at
the :doc:`API documentation<apidocs/yatiml>`, and if you get stuck, there is the
:doc:`problem_solving` section to help you out.
