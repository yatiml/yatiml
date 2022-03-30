.. image:: https://readthedocs.org/projects/yatiml/badge/?version=latest
    :target: https://yatiml.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Build Status

.. image:: https://github.com/yatiml/yatiml/workflows/continuous_integration/badge.svg
    :target: https://github.com/yatiml/yatiml/actions
    :alt: Build Status

.. image:: https://app.codacy.com/project/badge/Grade/bca7a121d9c742d2905eae08a75676c3
    :target: https://www.codacy.com/gh/yatiml/yatiml/dashboard
    :alt: Codacy Grade

.. image:: https://app.codacy.com/project/badge/Coverage/bca7a121d9c742d2905eae08a75676c3
    :target: https://www.codacy.com/gh/yatiml/yatiml/dashboard
    :alt: Code Coverage

.. image:: https://requires.io/github/yatiml/yatiml/requirements.svg?branch=master
    :target: https://requires.io/github/yatiml/yatiml/requirements/?branch=master
    :alt: Requirements Status

.. image:: https://zenodo.org/badge/147202299.svg
   :target: https://zenodo.org/badge/latestdoi/147202299

.. image:: https://img.shields.io/badge/rsd-yatiml-00a3e3.svg
   :target: https://www.research-software.nl/software/yatiml

################################################################################
YAtiML
################################################################################

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

YAtiML supports Python 3.6 and later.

If you use YAtiML for scientific work, we ask that you cite it. You can
`download a citation in various formats at the Research Software Directory
<https://www.research-software.nl/software/yatiml>`_.

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

#. use the `search functionality <https://github.com/yatiml/yatiml/issues>`_
   to see if someone already filed the same issue;
#. if your issue search did not yield any relevant results, make a new issue;
#. apply the "Question" label; apply other labels when relevant.

We'll answer your question, and improve the documentation where necessary.

Bugs
----

Like most software, YAtiML is made by humans, and we make mistakes. If you think
you've found a bug in YAtiML, please let us know! Reporting bugs goes as follows.

#. Use the `search functionality`_ to see if someone already filed the same
   issue.

#. If your issue search did not yield any relevant results, make a new issue.

   Please explain:
    - what you were trying to achieve,
    - what you did to make that happen,
    - what you expected the result to be,
    - what happened instead.

  It really helps to have the actual code for a simple example that demonstrates
  the issue, but excerpts and error messages and a description are welcome too.

#. Finally, apply any relevant labels to the newly created issue.

With that, we should be able to fix the problem.

License
*******

YAtiML is Copyright 2018-2022, Netherlands eScience Center, University of
Amsterdam, and VU University Amsterdam

Distributed under the Apache Software License 2.0.
