Basic Tutorial
==============

YAtiML is a library for reading and writing YAML from Python.

This tutorial shows how to use YAtiML by example. You can find the example
programs shown below in the ``docs/examples/`` directory in the repository.

A first example
---------------

Let's say that we're organising a drawing contest for kids, and are tracking
submissions in YAML files. We'll need to read the files into a Python program in
order to process them. Here's how to do that with YAtiML:

For the example to run, make sure that you have :ref:`installed YAtiML
<installing>` first.

.. literalinclude:: examples/load_any_yaml.py
  :caption: ``docs/examples/load_any_yaml.py``
  :language: python

If you run this program, it will output

.. code-block:: none

  ordereddict([('name', 'Janice'), ('age', 6)])


Here is the example again one line at a time.

.. code-block:: python

  import yatiml


This loads the YAtiML package, so that we can use it in our Python script.

.. code-block:: python

  yaml_text = (
          'name: Janice\n'
          'age: 6\n')


This makes a string with a YAML document in it. The parentheses are so we can
split the string over multiple lines, and we need a ``\n`` at the end of each
line to explicitly mark it as the end, otherwise everything will be glued
together on a single line and we end up with invalid YAML.

.. code-block:: python

  load = yatiml.load_function()


To load our document from the string, we need a load function. YAtiML doesn't
have a built-in load function. Instead, it makes a custom load function just for
you, if you call :meth:`yatiml.load_function`. We'll call the result ``load``.

This probably looks a bit funny, but it will become clear why we're doing this
in the next example.

.. code-block:: python

  doc = load(yaml_text)

  print(doc)


Here we call our shiny new load function to load the YAML into a Python object.
Then we print the result so that we can see what happened. We will get

.. code-block:: none

  ordereddict([('name', 'Janice'), ('age', 6)])


This again looks a bit funny, but this is almost the same thing as the
dictionary ``{'name': 'Janice', 'age': 6}`` that you probably expected.

Until recently, Python dictionaries held their entries in random order. For
accessing items that's not a problem, because you look them up based on the key
anyway. But having the lines of a YAML file reorganised in a random order can
make the file really hard to read! So YAtiML reads the file into a special
ordered dictionary, which preserves the order. That way, you can save it again
later without making a big mess. Otherwise it works just like a plain Python
``dict``, so you can do ``doc['name']`` and so on as usual.

Checking the input
------------------

In the example above, we didn't specify any constraints on what the input should
look like. This is often inconvenient. For example, if we have an age limit of
12 on our drawing contest and want to write a program that reads in the YAML
file for each submission, checks the age and then prints out the names of any
kids that are too old, then we really need to have both the name and the age in
each file, or it's not going to work.

The example code above will happily read any input. If there's a list of numbers
in the file, then ``doc`` will hold a list of numbers instead of a ``dict``, and
your program will probably crash somewhere with an error ``TypeError: list
indices must be integers or slices, not str`` and then you get to figure out
what went wrong and where.

It would be much better if we could check that our input is a really a
dictionary with keys ``name`` and ``age``. We could do that by hand, after
reading, but with YAtiML there's a better way to do it. We're going to make a
Python class that shows what the YAML should look like:

.. literalinclude:: examples/untyped_class.py
  :caption: ``docs/examples/untyped_class.py``
  :language: python


The main new bit of this example is the ``Submission`` class:

.. code-block:: python

  class Submission:
      def __init__(self, name, age):
          self.name = name
          self.age = age


This creates a Python class named ``Submission``. If you've never seen one, a
class is basically a group of variables, in this case ``name`` and ``age``.
Classes also have an *init function* with the special name ``__init__`` which is
used to create a variable containing an object holding those variables. So here
we have a class named ``Submission``. It can be used like this:

.. code-block:: python

  submission = Submission('Janice', 6)
  print(submission.name)    # prints Janice
  print(submission.age)     # prints 6

  submission.age = 7
  print(submission.age)     # prints 7


Now, we can pass this class to YAtiML when we ask it to create our load
function:

.. code-block:: python

  load = yatiml.load_function(Submission)


YAtiML will now create a load function for us that expects to read in a
dictionary containing keys ``name`` and ``age``.

We use the load function as before, and it will read the YAML file and convert
it into a ``Submission`` object. We can check that we really got one using
``type()``, and inspect the name and age of our contestant.

Of course, we got exactly the input we expected, so in this case everything went
fine. What if there's an error? Then you get an error message.

.. admonition:: Exercise

  Change the input in various ways in the previous example, and see what error
  messages you get when you try to load the incorrect input.


Checking types
--------------

If you have played around a little bit with the previous example, then you may
have noticed that there's a certain kind of problem that is not detected when
you load the YAML input into a ``Submission`` object, and that is that the
values for ``name`` and ``age`` may not be of the right type. For example,
someone could write their age as ``six`` instead of as ``6``, and you would
suddenly have a string where you expected a number. That would almost certainly
mess up the ``submission.age <= 12`` in your age check!

So it would be better if we could make sure that the inputs are of the right
type too, and give an error on loading if they are not. Here's how to do that:

.. literalinclude:: examples/typed_class.py
  :caption: ``docs/examples/untyped_class.py``
  :language: python


This example is almost the same as the previous one, except that the
``__init__`` function of our ``Submission`` class now has some *type
annotations*: instead of ``name`` it says ``name: str`` and instead of ``age``
it says ``age: int``. That is all it takes to make sure that any values given
for those keys in the YAML file are checked. (There's also ``-> None`` at the
end, which specifies that the function does not return anything. YAtiML ignores
this bit, and so can you if you want to.)

.. admonition:: Exercise

  Try changing the input to use values of a different type and see what happens.


``int`` and ``str`` are standard Python types, and adding them to the function
parameters as in the example is standard Python. For decimal numbers, you can
use ``float`` and for truth values (e.g. true, false, yes, no) the type
``bool``.

Lists and dicts are also supported, but they require some special types from the
standard Python ``typing`` package. For example, to allow multiple contestants
to make a drawing together, we could allow a list of strings for the ``name``
field, and a dictionary mapping each name to the corresponding age for ``age``.
That would look like this.

.. literalinclude:: examples/collaborative_submissions.py
  :caption: ``docs/examples/collaborative_submissions.py``
  :language: python


For dates you can use ``date`` from the ``datetime`` package, and if you need to
read the location of a file from a YAML file then you can use ``Path`` from
Python's ``pathlib``. If you want to explicitly accept any kind of YAML, then
you can use ``Any`` from ``typing``, which is the same as not specifying a type
at all like we did in the beginning.

Finally, ``Union`` from ``typing`` makes it possible to accept multiple
different types. Try this for example:

.. literalinclude:: examples/custom_class.py
  :caption: ``docs/examples/custom_class.py``
  :language: python


and see what YAML inputs it will accept.

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
have a look at saving objects back to YAML, or dumping as PyYAML call it. The
code for this is a mirror image of the loading code:

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
it would be nice to do full round-trip formatting of the input YAML, the PyYAML
library used by YAtiML does not support this, so for now this is what YAtiML
does.

:meth:`yatiml.dumps_function` creates a function that converts objects to a
string. If you want to write the output to a file directly, you can use
:meth:`yatiml.dump_function` instead to create a function that can do that.

As an example of the advantage of using YAtiML, saving a Submission document
with PyYAML or ruamel.yaml gives this:

.. code-block:: none

  !!python/object:__main__.Submission {age: 7, name: Youssou, tool: pencils}

which is not nearly as nice to read or write. (To be fair, ruamel.yaml can do a
bit nicer than this with its RoundTripDumper, but the tag with the exclamation
marks remains.)

Saving to JSON
--------------

YAML is a superset of JSON, so YAtiML can read JSON files. If you want to save
JSON as well, then you can use :meth:`yatiml.dumps_json_function` instead:

.. code-block:: python

  # Create dumper
  dumps = yatiml.dumps_json_function(Submission)
