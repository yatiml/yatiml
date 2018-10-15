.. _development:

Development
***********

To install yatiml in development mode, do:

.. code-block:: console

  git clone git@github.com:yatiml/yatiml.git
  cd yatiml
  pip install -e .[dev]

The -e option links the installed files to the source files in the repository,
rather than copying them, so that changes are reflected immediately in the
installed copy. The additional ``[dev]`` installs the development tools, which
you can then use as follows.

Run tests (including coverage and type checking) with:

.. code-block:: console

  python setup.py test


A local copy of the documentation can be generated using:

.. code-block:: console

  python setup.py build_sphinx


Contributing
------------

If you want to contribute some improvements to YAtiML, please use the following
process:

#. (**important**) Announce your plan to the rest of the community *before you
   start working*. This announcement should be in the form of a (new) issue.
#. (**important**) wait until some kind of consensus is reached about your idea
   being a good idea.
#. If needed, fork the repository to your own Github profile and create your
   own feature branch off of the latest master commit. While working on your
   feature branch, make sure to stay up to date with the master branch by
   pulling in changes, possibly from the 'upstream' repository (follow the
   instructions `here
   <https://help.github.com/articles/configuring-a-remote-for-a-fork/>`__ and
   `here <https://help.github.com/articles/syncing-a-fork/>`__).
#. Make sure the existing tests still work by running ``python setup.py test``.

#. Add your own tests (if necessary).

#. Update or expand the documentation.

#. Use ``yapf`` to fix the readability of your code style and ``isort``
   to format and group your imports.

#. `Push <http://rogerdudler.github.io/git-guide/>`_ your feature branch to
   (your fork of) the YAtiML repository on GitHub; 1. create the pull request,
   e.g. following the instructions `here
   <https://help.github.com/articles/creating-a-pull-request/>`_.

In case you feel like you've made a valuable contribution, but you don't know
how to write or run tests for it, or how to generate the documentation: don't
let this discourage you from making the pull request; we can help you! Just go
ahead and submit the pull request, but keep in mind that you might be asked to
append additional commits to your pull request.


Making a release
****************

YAtiML uses Git on GitHub for version management, using the `Git Flow`_
branching model. Making a release involves quite a few steps, so they're listed
here to help make the process more reliable; this information is really only
useful for the maintainers.

Make release branch
-------------------

To start the release process, make a release branch

.. code-block:: bash

  git checkout -b release-x.y.z develop

YAtiML uses `Semantic Versioning`_, so name the new version accordingly.

Update version
--------------

Next, the version should be updated. There is a version tag in ``setup.py`` and
two for the documentation in ``docs/conf.py`` (search for ``version`` and
``release``). On the development branch, these should be set to ``develop``. On
the release branch, they should be set to ``x.y.z`` (or rather, the actual
number of this release of course).

Check documentation
-------------------

Since we've just changed the documentation build configuration, the build should
be run locally to test:

.. code-block:: bash

  python setup.py build_sphinx

It may give some warnings about missing references; they should disappear if
you run the command a second time. Next, point your web browser to
``docs/_build/html/index.html`` and verify that the documentation built
correctly. In particular, the new version number should be in the browser's
title bar as well as in the blue box on the top left of the page.

Run tests
---------

Before we make a commit, the tests should be run, and this is a good idea anyway
if we're making a release. So run ``python setup.py test`` and check that
everything is in order.

Commit the version update
-------------------------

That's easy:

.. code-block:: bash

  git commit -m 'Set release version'
  git push

This will trigger the Continuous Integration, so check that that's not giving
any errors while we're at it.

Merge into the master branch
----------------------------

If all seems to be well, then we can merge the release branch into the master
branch and tag it, thus making a release, at least as far as Git Flow is
concerned.

.. code-block:: bash

  git checkout master
  git merge --no-ff release-x.y.z
  git tag -a x.y.z
  git push

Build and release to PyPI
-------------------------

Finally, the new version needs to be built and uploaded to PyPI, so that people
can start using it. To build, use:

.. code-block:: bash

  python3 setup.py sdist bdist_wheel

Then, we can upload to the test instance of PyPI:

.. code-block:: bash

  twine upload --repository-url https://test.pypi.org/legacy/ dist/*

To test that we can install it, run this in a fresh virtualenv:

.. code-block:: bash

  python3 -m pip install --index-url https://test.pypi.org/simple/ yatiml

And if all seems well, we can upload to the real PyPI:

.. code-block:: bash

  twine upload dist/*

.. _`Git Flow`: http://nvie.com/posts/a-successful-git-branching-model/
.. _`Semantic Versioning`: http://www.semver.org
