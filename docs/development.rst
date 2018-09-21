Development
***********

YAtiML is developed on GitHub, from where you can clone the repository using

``git clone https://github.com/yatiml/yatiml.git``

Tests can be run with ``python setup.py test``, and static type checks can be
performed by running ``mypy yatiml`` and ``mypy tests`` from the top level
directory.

A local copy of the documentation can be generated using ``python setup.py
build_sphinx``.


Coding style conventions and code quality
-----------------------------------------

* You may need run ``pip install .[dev]`` first, to install the required dependencies
* You can use ``yapf`` to fix the readability of your code style and ``isort`` to format and group your imports
* `Relevant section in the guide <https://guide.esciencecenter.nl/best_practices/language_guides/python.html#coding-style-conventions>`_



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

