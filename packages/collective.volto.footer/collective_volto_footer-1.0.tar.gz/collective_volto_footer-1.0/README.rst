.. This README is meant for consumption by humans and PyPI. PyPI can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on PyPI or github. It is a comment.

.. image:: https://github.com/collective/collective.volto.footer/actions/workflows/plone-package.yml/badge.svg
    :target: https://github.com/collective/collective.volto.footer/actions/workflows/plone-package.yml

.. image:: https://coveralls.io/repos/github/collective/collective.volto.footer/badge.svg?branch=main
    :target: https://coveralls.io/github/collective/collective.volto.footer?branch=main
    :alt: Coveralls

.. image:: https://codecov.io/gh/collective/collective.volto.footer/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/collective/collective.volto.footer

.. image:: https://img.shields.io/pypi/v/collective.volto.footer.svg
    :target: https://pypi.python.org/pypi/collective.volto.footer/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/collective.volto.footer.svg
    :target: https://pypi.python.org/pypi/collective.volto.footer
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/pyversions/collective.volto.footer.svg?style=plastic   :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/l/collective.volto.footer.svg
    :target: https://pypi.python.org/pypi/collective.volto.footer/
    :alt: License


=======================
collective.volto.footer
=======================

Backend add-on for Plone that provides editable footer functionality for Volto sites.



https://github.com/user-attachments/assets/64b0b329-86f2-4dfd-afc6-742b0802f051


This backend add-on provides the necessary behaviors and content types to make footers editable in Volto sites. It allows you to customize footers by adding blocks to them, with context-aware footer selection based on the current page location.

**Requirements:**
- This backend add-on requires `volto-footer <https://github.com/collective/volto-footer>`_ to be installed on the frontend.

Features
--------

- **Editable Footer Behavior**: Adds behavior to make content types support editable footers
- **Context-aware Footer Selection**: Automatically selects the most appropriate footer based on page location  
- **Block-based Footer Content**: Supports any type of Volto blocks in footer content
- **Flexible Configuration**: The editable footer behavior can be activated on any content type

Examples
--------

This add-on works together with the volto-footer frontend package to provide:
- Customizable footer content using Volto blocks
- Hierarchical footer inheritance based on content location
- Easy management of footer content through the Plone interface

Installation
------------

Install collective.volto.footer by adding it to your buildout::

    [buildout]

    ...

    eggs =
        collective.volto.footer


and then running ``bin/buildout``


Authors
-------

Provided by awesome people ;)


Contributors
------------

Put your name here, you deserve it!

- ?


Contribute
----------

- Issue Tracker: https://github.com/collective/collective.volto.footer/issues
- Source Code: https://github.com/collective/collective.volto.footer
- Documentation: https://docs.plone.org/foo/bar


Support
-------

If you are having issues, please let us know.
We have a mailing list located at: project@example.com


License
-------

The project is licensed under the GPLv2.
