.. _installing:

Installing YAtiML
=================

YAtiML is available from PyPI, and you can install it using pip:

.. code-block:: console

  pip install yatiml


or add it to the dependencies of your project in your usual way.

Conda
-----

If you're using conda, then you should *not* install via ``pip``, because this
will result in a broken install and import errors, due to a bug in Anaconda.
Instead, you should install YAtiML from conda-forge:

.. code-block:: console

  conda install -c conda-forge yatiml


Changes between versions are listed in the file CHANGELOG.rst. YAtiML adheres
to `Semantic Versioning <http://semver.org/>`_. Starting from version 1.0, you
will be able to count on a stable API as long as you pin your dependency to a
major version.
