.. _development:

Development
***********

To get the source code from GitHub, you can do

.. code-block:: console

  git clone git@github.com:yatiml/yatiml.git
  cd yatiml


Run tests (including coverage and type checking) with:

.. code-block:: console

  pip install tox
  tox


A local copy of the documentation can be generated using:

.. code-block:: console

  tox -e docs


Contributing
------------

If you want to contribute some improvements to YAtiML, please use the following
process:

#. (**important**) Announce your plan to the rest of the community *before you
   start working*. This announcement should be in the form of a (new) issue.
#. (**important**) wait until some kind of consensus is reached about your idea
   being a good idea.
#. If needed, fork the repository to your own Github profile and create your
   own feature branch off of the latest ``develop`` commit. While working on
   your feature branch, make sure to stay up to date with the ``develop``
   branch by pulling in changes, possibly from the 'upstream' repository
   (follow the instructions `here
   <https://help.github.com/articles/configuring-a-remote-for-a-fork/>`__ and
   `here <https://help.github.com/articles/syncing-a-fork/>`__).
#. Make sure the existing tests still work by running ``python setup.py test``.

#. Add your own tests (if necessary).

#. Update or expand the documentation.

#. Use ``yapf`` to fix the readability of your code style and ``isort``
   to format and group your imports.

#. `Push <http://rogerdudler.github.io/git-guide/>`_ your feature branch to
   (your fork of) the YAtiML repository on GitHub.

#. create the pull request,
   e.g. following the instructions `here
   <https://help.github.com/articles/creating-a-pull-request/>`_.

In case you feel like you've made a valuable contribution, but you don't know
how to write or run tests for it, or how to generate the documentation: don't
let this discourage you from making the pull request; we can help you! Just go
ahead and submit the pull request, but keep in mind that you might be asked to
append additional commits to your pull request.


Making a release
----------------

YAtiML uses Git on GitHub for version management, using the `Git Flow`_
branching model. Making a release involves quite a few steps, so they're listed
here to help make the process more reliable; this information is really only
useful for the maintainers.

Check metadata
--------------

- Check the metadata in ``setup.py``, and update as necessary.

- Check the copyright date and owners in README.rst and docs/conf.py and update
  as necessary.


Update the changelog
....................

Each release should have an entry in the CHANGELOG.rst describing the new
features and fixed problems. Since we'll want to carry these entries forward,
we'll make them first, on the develop branch. Use the git log to get a list of
the changes, and switch to the development branch:

.. code-block:: bash

  git log <your favourite options>
  git checkout develop

and then edit CHANGELOG.rst and commit.

.. code-block:: bash

  git add CHANGELOG.rst
  git commit -m 'Add version x.y.z to the change log'

Make release branch
...................

To start the release process, make a release branch

.. code-block:: bash

  git checkout -b release-x.y.z develop

YAtiML uses `Semantic Versioning`_, so name the new version accordingly.

Update version
..............

Next, the version should be updated. There is a version tag in ``setup.py`` and
two for the documentation in ``docs/conf.py`` (search for ``version`` and
``release``). There is also an ``__version__`` in ``__init__.py``. On the
development branch, these should be set to ``x.y.z.dev0``, where ``x.y.z`` is
the expected next version. On the release branch, they should be set to
``x.y.z`` (with here the actual number of this release of course).

Check documentation
...................

Since we've just changed the documentation build configuration, the build should
be run locally to test:

.. code-block:: bash

  tox -e docs

It may give some warnings about missing references; they should disappear if
you run the command a second time. Next, point your web browser to
``docs/_build/html/index.html`` and verify that the documentation built
correctly. In particular, the new version number should be in the browser's
title bar as well as in the blue box on the top left of the page.

Run tests
.........

Before we make a commit, the tests should be run, and this is a good idea anyway
if we're making a release. So run ``tox`` and check that everything is in order.

Commit the version update
.........................

This is the usual Git poem:

.. code-block:: bash

  git add setup.py docs/conf.py yatiml/__init__.py
  git commit -m 'Set release version to x.y.z'
  git push --set-upstream origin release-x.y.z

This will trigger the Continuous Integration, so check that that's not giving
any errors while we're at it.

Fix badges
..........

The badges in the README.rst normally point to the development branch versions
of everything. For the master branch, they should point to the master version.
Note that for the ReadTheDocs badge, `develop` should be changed to `latest`,
and that for Codacy there is only one badge, so no change is needed.

.. code-block:: bash

  # edit README.rst
  git add README.rst
  git commit -m 'Update badges to point to master'
  git push

Merge into the master branch
............................

If all seems to be well, then we can merge the release branch into the master
branch and tag it, thus making a release, at least as far as Git Flow is
concerned. We use the ``-X theirs`` option here to resolve the merge conflict
caused by the version update that was done for the previous release, which we
don't have on this branch. The last command is to push the tag, which is
important for GitHub and GitHub integrations.

.. code-block:: bash

  git checkout master
  git merge --no-ff -X theirs release-x.y.z
  git tag -a x.y.z -m 'Release x.y.z'
  git push
  git push origin x.y.z

Build and release to PyPI
.........................

Finally, the new version needs to be built and uploaded to PyPI, so that people
can start using it. To build, use:

.. code-block:: bash

  python3 setup.py sdist bdist_wheel

Then, we can upload to the test instance of PyPI:

.. code-block:: bash

  twine upload --repository-url https://test.pypi.org/legacy/ dist/yatiml-x.y.z*

To test that we can install it, run this in a fresh virtualenv:

.. code-block:: bash

  python3 -m pip install --index-url https://test.pypi.org/simple/ yatiml

And if all seems well, we can upload to the real PyPI:

.. code-block:: bash

  twine upload dist/yatiml-x.y.z*

Make a GitHub Release
.....................

Go to Releases on the GitHub page and make a new release from the tag. For the
release notes, copy-paste from the CHANGELOG and convert from RST to Markdown.

Merge release branch back into develop
......................................

To continue developing, merge the release branch back into develop

.. code-block:: bash

  git checkout develop
  git merge --no-commit release-x.y.z
  git push

Make sure that the badges are set to develop, and that the version number is
set to the next expected version x.y.{z+1}.dev (it's fine if x.{y+1}.0 is what
ends up being released eventually). Then you can commit and continue developing.

.. _`Git Flow`: http://nvie.com/posts/a-successful-git-branching-model/
.. _`Semantic Versioning`: http://www.semver.org
