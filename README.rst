.. image:: https://readthedocs.org/projects/yatiml/badge/?version=latest
    :target: https://yatiml.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Build Status

.. image:: https://api.travis-ci.org/yatiml/yatiml.svg?branch=develop
    :target: https://travis-ci.org/yatiml/yatiml
    :alt: Build Status

.. image:: https://api.codacy.com/project/badge/Grade/e9cf088f3f6d44cc82fd6aead08202e1
    :target: https://www.codacy.com/app/LourensVeen/yatiml
    :alt: Codacy Grade

.. image:: https://api.codacy.com/project/badge/Coverage/e9cf088f3f6d44cc82fd6aead08202e1
    :target: https://www.codacy.com/app/LourensVeen/yatiml
    :alt: Code Coverage

.. image:: https://requires.io/github/yatiml/yatiml/requirements.svg?branch=develop
    :target: https://requires.io/github/yatiml/yatiml/requirements/?branch=develop
    :alt: Requirements Status

################################################################################
YAtiML
################################################################################

YAtiML is a small Python library that works with ruamel.yaml, adding functions
for automatic type recognition to it. YAtiML is not a schema language like XSD
and Relax-NG are for XML, or JSON Schema is for JSON. YAtiML is also not an
Object/YAML mapper (YAML is already an object serialisation system, so you don't
need an extra library for that). However, YAtiML does solve the same kind of
problems, and more, so if you are looking for a schema language for YAML, YAtiML
may actually be what you need.

If you use YAtiML for scientific work, we ask that you cite it. We have provided
a CITATION.cff file to help you do so quickly and easily.


How it works
************

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

With YAtiML, you describe your file format by defining a set of ordinary Python
classes. You then create a Loader class, which you can then use with the normal
ruamel.yaml.load(). However, objects of the types you have defined will now be
recognised automatically in the input YAML text, a type check will be performed
so that you can be sure that you're getting what you were expecting, and the
resulting data structure will consist of instances of your classes. Also, with a
few lines of extra code, you can add some syntactic sugar to the YAML text
format, making it easier for your users to write files in your format by hand in
a variety of ways, while you still get consistent objects. Of course, YAtiML
supports the reverse as well, making a Dumper for you to use with yaml.dump(),
which ensures an easy-to-read, clean YAML output.

There are still some limitations on round-tripping data, so reading a YAML file
and then saving it again may change the order of attributes, and will strip
comments. Round-trip support is still in development in ruamel.yaml, and there
is not much YAtiML can do to improve this at the moment. YAtiML does contribute
a small but important feature to generating YAML files by your software:
attributes will be written out in the order in which you've defined them, rather
than in random order, which really improves the readability of the result
(assuming that the order of your definition is logical, of course.)

YAtiML supports Python 3.4 and later.


Documentation and Help
**********************

Instructions on how to install and use YAtiML can be found in `the YAtiML
documentation <https://yatiml.readthedocs.io>`_.

Code of Conduct
---------------

Before describing where to ask questions or report bugs, we'd like to point out
that this project is governed by a code of conduct, as described in
CODE_OF_CONDUCT.rst, and we expect you to adhere to it. Please be nice to your
fellow humans.

Questions
---------

If you have a question that the documentation does not answer for you, then you
have found a bug in the documentation. We'd love to fix it, but we need a bit of
help from you to do so. Please do the following:

1. use the search functionality `here <https://github.com/yatiml/yatiml/issues>`_
   to see if someone already filed the same issue;
1. if your issue search did not yield any relevant results, make a new issue;
1. apply the "Question" label; apply other labels when relevant.

We'll answer your question, and improve the documentation where necessary.

Bugs
----

Like most software, YAtiML is made by humans, and we make mistakes. If you think
you've found a bug in YAtiML, please let us know! Reporting bugs goes as follows.

1. Use the search functionality `here <https://github.com/yatiml/yatiml/issues>`_
  to see if someone already filed the same issue.
1. If your issue search did not yield any relevant results, make a new issue.
   Please explain:
    - what you were trying to achieve,
    - what you did to make that happen,
    - what you expected the result to be,
    - what happened instead.
  It really helps to have the actual code for a simple example that demonstrates
  the issue, but excerpts and error messages and a description are welcome too.
1. Finally, apply any relevant labels to the newly created issue.

With that, we should be able to fix the problem.

License
*******

YAtiML is Copyright 2018, Netherlands eScience Center, University of Amsterdam,
and VU University Amsterdam

Distributed under the Apache Software License 2.0.
