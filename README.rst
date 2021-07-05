========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis|
        |
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/forge/badge/?style=flat
    :target: https://forge.readthedocs.io/
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.com/FarhadMaleki/forge.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.com/github/FarhadMaleki/forge

.. |version| image:: https://img.shields.io/pypi/v/forge.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/forge

.. |wheel| image:: https://img.shields.io/pypi/wheel/forge.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/forge

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/forge.svg
    :alt: Supported versions
    :target: https://pypi.org/project/forge

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/forge.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/forge

.. |commits-since| image:: https://img.shields.io/github/commits-since/FarhadMaleki/forge/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/FarhadMaleki/forge/compare/v0.0.0...master



.. end-badges

A package for 3D image augmentation

* Free software: GNU Lesser General Public License v3 (LGPLv3)

Installation
============

::

    pip install forge

You can also install the in-development version with::

    pip install https://github.com/FarhadMaleki/forge/archive/master.zip


Documentation
=============


https://forge.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
