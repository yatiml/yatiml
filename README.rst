################################################################################
YAtiML
################################################################################

YAtiML is a small Python library that works with yaml or ruamel.yaml, adding
functions for automatic type recognition to it. YAtiML is not a schema language
like XSD and Relax-NG are for XML, or JSON Schema is for JSON. As YAML is not a
document format, a schema language for it does not make much sense. YAtiML does
solve the same kind of problems however, and more, so if you are looking for a
schema language for YAML, YAtiML may actually be what you need.

How it works
************

YAML-based file formats can be very handy, as YAML is easy to write by humans,
and parsing support for it is widely available. Just read your YAML file into a
document structure (a tree of nested dicts and lists), and manipulate that in
your code.

While this works fine for simple file formats, it does not scale very well to
more complex file formats such as the Common Workflow Language or the Multiscale
Computing Language (yMCL). Manual error-checking is lots of work and
error-prone, defaults are not set automatically (which is especially tricky if
you have multiple nested optional objects), and the file format often ends up
somewhat underspecified.

Furthermore, a small collection of nested dicts and lists may work fine, but for
more complex file formats, this becomes unwieldy and a set of objects is a
better choice. Although it is not often used this way, YAML is actually a fully
fledged object-to-text serialisation protocol. The Python yaml and ruamel.yaml
libraries will actually construct objects for you, but the class names need to
be put in the YAML file for that to work, which makes those files harder to
write for humans.

With YAtiML, you describe your file format by defining a set of ordinary Python
classes. You pass these classes to YAtiML, which constructs a Loader for you
that you can then use with the normal yaml.load(). However, objects of the types
you have defined will now be recognised automatically in the input YAML text,
and the result will contain those objects. Also, with a few lines of extra code,
you can add some syntactic sugar to the YAML text format, making it easier for
your users to write files in your format by hand in a variety of ways, while you
still get consistent objects. Of course, YAtiML supports the reverse as well,
making a Dumper for you to user with yaml.dump().

Project Setup
*************

Here we provide some details about the project setup. Most of the choices are explained in the `guide <https://guide.esciencecenter.nl>`_. Links to the relevant sections are included below.
Feel free to remove this text when the development of the software package takes off.

For a quick reference on software development, we refer to `the software guide checklist <https://guide.esciencecenter.nl/best_practices/checklist.html>`_.

Testing and code coverage
-------------------------

* Tests should be put in the ``tests`` folder.
* The testing framework used is `PyTest <https://pytest.org>`_

  - `PyTest introduction <http://pythontesting.net/framework/pytest/pytest-introduction/>`_

* Tests can be run with ``python setup.py test``

  - This is configured in ``setup.py`` and ``setup.cfg``

* Use `Travis CI <https://travis-ci.com/>`_ to automatically run tests and to test using multiple Python versions

  - Configuration can be found in ``.travis.yml``
  - `Getting started with Travis CI <https://docs.travis-ci.com/user/getting-started/>`_

* TODO: add something about code quality/coverage tool?
* `Relevant section in the guide <https://guide.esciencecenter.nl/best_practices/language_guides/python.html#testing>`_

Documentation
-------------

* Documentation should be put in the ``docs`` folder. The contents have been generated using ``sphinx-quickstart`` (Sphinx version 1.6.5).
* We recommend writing the documentation using Restructured Text (reST) and Google style docstrings.

  - `Restructured Text (reST) and Sphinx CheatSheet <http://openalea.gforge.inria.fr/doc/openalea/doc/_build/html/source/sphinx/rest_syntax.html>`_
  - `Google style docstring examples <http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`_.

* To generate html documentation run ``python setup.py build_sphinx``

  - This is configured in ``setup.cfg``
  - Alternatively, run ``make html`` in the ``docs`` folder.

* The ``docs/_static`` and ``docs/_templates`` contain an (empty) ``.gitignore`` file, to be able to add them to the repository. These two files can be safely removed (or you can just leave them there).
* To put the documentation on `Read the Docs <https://readthedocs.org>`_, log in to your Read the Docs account, and import the repository (under 'My Projects').

  - Include the link to the documentation in this README_.

* `Relevant section in the guide <https://guide.esciencecenter.nl/best_practices/language_guides/python.html#writingdocumentation>`_

Coding style conventions and code quality
-----------------------------------------

* Check your code style with ``prospector``
* You may need run ``pip install .[dev]`` first, to install the required dependencies
* You can use ``yapf`` to fix the readability of your code style and ``isort`` to format and group your imports
* `Relevant section in the guide <https://guide.esciencecenter.nl/best_practices/language_guides/python.html#coding-style-conventions>`_

CHANGELOG.rst
-------------

* Document changes to your software package
* `Relevant section in the guide <https://guide.esciencecenter.nl/software/releases.html#changelogmd>`_

CITATION.cff
------------

* To allow others to cite your software, add a ``CITATION.cff`` file
* It only makes sense to do this once there is something to cite (e.g., a software release with a DOI).
* To generate a CITATION.cff file given a DOI, use `doi2cff <https://github.com/citation-file-format/doi2cff>`_.
* `Relevant section in the guide <https://guide.esciencecenter.nl/software/documentation.html#citation-file>`_

CODE_OF_CONDUCT.rst
-------------------

* Information about how to behave professionally
* `Relevant section in the guide <https://guide.esciencecenter.nl/software/documentation.html#code-of-conduct>`_

CONTRIBUTING.rst
----------------

* Information about how to contribute to this software package
* `Relevant section in the guide <https://guide.esciencecenter.nl/software/documentation.html#contribution-guidelines>`_

MANIFEST.in
-----------

* List non-Python files that should be included in a source distribution
* `Relevant section in the guide <https://guide.esciencecenter.nl/best_practices/language_guides/python.html#building-and-packaging-code>`_

NOTICE
------

* List of licenses of the project and dependencies
* `Relevant section in the guide <https://guide.esciencecenter.nl/best_practices/licensing.html#notice>`_

Installation
------------

To install yatiml, do:

.. code-block:: console

  git clone git@github.com:yatiml/yatiml.git
  cd yatiml
  pip install .


Run tests (including coverage) with:

.. code-block:: console

  python setup.py test


Documentation
*************

.. _README:

Include a link to your project's full documentation here.

Contributing
************

If you want to contribute to the development of YAtiML,
have a look at the `contribution guidelines <CONTRIBUTING.rst>`_.

License
*******

Copyright 2018, Netherlands eScience Center, University of Amsterdam, and VU
University Amsterdam

Apache Software License 2.0
