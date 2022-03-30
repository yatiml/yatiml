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

Next, point your web browser to ``docs/_build/index.html`` and verify that the
documentation built correctly. In particular, the new version number should be
in the browser's title bar as well as in the blue box on the top left of the
page.

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
Note that for the ReadTheDocs badge, ``develop`` should be changed to
``latest``, and that for Codacy there is only one badge, so no change is needed.

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

To test that we can install it, run this in a fresh virtualenv. Note that the
PyPI test server doesn't have the dependencies, so we need to install those from
the production server first.

.. code-block:: bash

  pip install 'ruamel.yaml<0.17' typing_extensions
  pip install --index-url https://test.pypi.org/simple/ yatiml

And if all seems well, we can upload to the real PyPI:

.. code-block:: bash

  twine upload dist/yatiml-x.y.z*

Update conda-forge feedstock
............................

(Note: we're skipping a local rerender here in favour of letting the conda-forge
bot handle it on GitHub. If that becomes an issue we'll change it, but this way
we don't need to have conda installed locally.)

First, we need a fork of https://github.com/conda-forge/yatiml-feedstock, so
create one if you don't have one yet, and clone it locally. Then

.. code-block:: bash

  git checkout main
  git pull
  git checkout -b release-x.y.z

This creates a branch to work on. Next, we need to get a checksum for the
package we uploaded to PyPI. In the main yatiml directory, run:

.. code-block:: bash

  sha256sum dist/yatiml-x.y.z.tar.gz

Next, in ``yatiml-feedstock``, edit ``recipe/meta.yaml``:

- Update to the new version at the top
- Replace the checksum with the one for the new release

We can then test the new build by running ``python3 build-locally.py``. This
will build the package inside of a Docker container, so you need to have Docker
installed and have a couple GB of free disk space.

If it all works, then we can commit the changes to the local branch:

.. code-block:: bash

  git add recipe/meta.yaml
  git commit -m 'Update to version x.y.z'
  git push --set-upstream origin release-x.y.z

Note that this pushes to the fork, not to ``conda-forge/yatiml-feedstock``,
which is exactly what we want. Pushing to upstream directly will break the
automation.

Instead, go to the fork, and make a pull request for merging the changes into
``conda-forge/yatiml-feedstock:main``. Run through the checklist in the
template. To check whether the license file is included, in the yatiml
directory do:

.. code-block:: bash

  tar tf dist/yatiml-x.y.z.tar.gz

and check that LICENSE and NOTICE are both there.

Add a ``@conda-forge-admin, please rerender`` to the text to rerender the
feedstock. This will upgrade the auto-generated parts of ``meta.yaml`` to the
latest configuration, so it adds another commit to the branch.

So, wait for the ``conda-forge-linter`` to lint, and for ``conda-forge-admin``
to rerender, and then merge the PR using the GitHub GUI. The new package will
now be staged and built and copied over to the Anaconda repository. This may
take a couple of hours, so don't worry if it doesn't appear immediately.

As a final test, you can do:

.. code-block:: bash

  docker run -ti conda/miniconda3
  # conda install -c conda-forge yatiml

which should install the new version.

Make a GitHub Release
.....................

Go to Releases on the GitHub page and make a new release from the tag. For the
release notes, use this template and copy-paste the content from the CHANGELOG:

.. code-block:: markdown

  # YAtiML
  YAML-based file formats can be very handy, as YAML is easy to write by humans, and parsing support for it is widely available. Just read your YAML file into a document structure (a tree of nested dicts and lists), and manipulate that in your code.

  As long as that YAML file contains exactly what you expect, that works fine. But if it contains a mistake, then you're likely to crash the program with a cryptic error message, or worse (especially if the YAML file was loaded from the Internet) it may do something unexpected.

  To avoid that, you can validate your YAML using various schema checkers. You write a description of what your YAML file must look like, then feed that to a library which checks the incoming file against the description. That gives you a better error message, but it's a lot of work.

  YAtiML takes a different approach. Instead of a schema, you write a Python class. You probably already know how to do that, so no need to learn anything. YAtiML then generates loading and dumping functions for you, which convert between YAML and Python objects. If needed, you can add some extra code to make the YAML look nicer or implement special features.

  # <x.y.z>

  ## Incompatible changes
  * <change>

  ## New functionality
  * <new>

  ## Fixes
  * <fixed>

  ## Removed
  * <removed>

The preamble is there because this text ends up on the Zenodo page, and people
who end up there will probably want to know what it is before learning about the
latest changes.

There's no need to upload binaries, GitHub will create tar files with snapshots
for Zenodo automatically, and we've already put things on PyPI and Conda.

Merge release branch back into develop
......................................

To continue developing, merge the release branch back into develop

.. code-block:: bash

  git checkout develop
  git merge --no-commit release-x.y.z

Make sure that the badges are set to develop, and that the version number is
set to the next expected version x.y.{z+1}.dev (it's fine if x.{y+1}.0 is what
ends up being released eventually). Then you can commit and continue developing:

.. code-block:: bash

  git commit
  git push

Update issues
.............

Go through the issues on GitHub and close the ones for which a fix was released.
Or if they were created by someone else, ask the user to check that the new
version solves their problem and then close the issue if it does.

.. _`Git Flow`: http://nvie.com/posts/a-successful-git-branching-model/
.. _`Semantic Versioning`: http://www.semver.org
