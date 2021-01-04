.. YAtiML documentation master file, created by
   sphinx-quickstart on Thu Jun 21 11:07:11 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to YAtiML
=================

YAML-based file formats can be very handy, as YAML is easy to write by humans,
and parsing support for it is widely available. Just read your YAML file into a
document structure (a tree of nested dicts and lists), and manipulate that in
your code.

As long as that YAML file contains exactly what you expect, that works fine.
But if it contains a mistake, then you're likely to crash the program with a
cryptic error message, or worse (especially if the YAML file was loaded from the
Internet) it may do something unexpected.

To avoid that, you can validate your YAML using various schema checkers. You
write a description of what your YAML file must look like, then feed that to a
library which checks the incoming file against the description. That gives you a
better error message, but it's a lot of work.

YAtiML takes a different approach. Instead of a schema, you write a Python
class. You probably already know how to do that, so no need to learn anything.
YAtiML then generates loading and dumping functions for you, which convert
between YAML and Python objects. If needed, you can add some extra code to make
the YAML look nicer or implement special features.

YAtiML supports Python 3.5 and later.

If you use YAtiML for scientific work, we ask that you cite it. You can
`download a citation in various formats at the Research Software Directory
<https://www.research-software.nl/software/yatiml>`_.


Documentation Overview
======================

.. toctree::
   :maxdepth: 2

   why
   installation
   basic_tutorial
   advanced_features
   recipes
   problem_solving
   api


Development
===========

.. toctree::
  :maxdepth: 2

  development


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
