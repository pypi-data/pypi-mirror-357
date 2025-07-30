Maintainers: How to make a new release?
---------------------------------------

*Fixed font text area below list commands expected to be entered in a bash shell*

1. Make sure the cli and module work as expected.

2. Choose the next release version number:

::

    release="X.Y.Z"

3. Tag the release and push:

*If you don't have a GPG key, omit the ``-s`` option.*

::

    git tag -s -m "hdmf-docutils ${release}" ${release} origin/main
    git push origin ${release}

4. Create a new release on the GitHub UI and the `publish_pypi.yml` workflow will automatically upload the packages to PyPI.

Maintainers: How to manually upload packages to PyPI?
-----------------------------------------------------

5. Configure ``~/.pypirc`` as described `here <https://packaging.python.org/en/latest/tutorials/packaging-projects/#uploading-your-project-to-pypi>`_.

6. Create the source tarball and wheel:

::

    rm -rf dist/
    python -m pip install build
    python -m build 

7. Upload the packages to the testing PyPI instance:

::

    pip install --upgrade twine
    twine upload -r testpypi dist/*

Check the `PyPI testing package page <https://test.pypi.org/project/hdmf-docutils/>`_.

8. Upload the packages to the PyPI instance::

::

    twine upload dist/*

Check the `PyPI package page <https://pypi.org/project/hdmf-docutils/>`_.
