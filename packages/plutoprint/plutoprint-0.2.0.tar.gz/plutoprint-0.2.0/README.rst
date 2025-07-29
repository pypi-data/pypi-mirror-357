|build| |docs| |license| |downloads| |pypi| |pyver|

PlutoPrint
==========

PlutoPrint is a lightweight and easy-to-use Python library for generating high-quality PDFs and images directly from HTML or XML content. It is based on `PlutoBook’s <https://github.com/plutoprint/plutobook>`_ robust rendering engine and provides a simple API to convert your HTML into crisp PDF documents or vibrant image files. This makes it ideal for reports, invoices, or visual snapshots.

Installation
------------

.. code-block:: bash

   pip install plutoprint

PlutoPrint depends on `PlutoBook <https://github.com/plutoprint/plutobook>`_. For faster builds, it is highly recommended to `install PlutoBook and its dependencies manually <https://github.com/plutoprint/plutobook?tab=readme-ov-file#installation-guide>`_ beforehand. Otherwise, Meson will build them from source during installation, which can significantly increase build time.

For Windows 64-bit users, PlutoPrint provides prebuilt binaries, so no additional setup is required.

Quick Usage
-----------

.. code-block:: python

   import plutoprint

   book = plutoprint.Book(plutoprint.PAGE_SIZE_A4)
   book.load_html("<b> Hello World </b>")
   book.write_to_pdf("hello.pdf")

Links & Resources
-----------------

- Documentation: https://plutoprint.readthedocs.io
- Samples: https://github.com/plutoprint/plutoprint-samples
- Code: https://github.com/plutoprint/plutoprint
- Issues: https://github.com/plutoprint/plutoprint/issues
- Donation: https://github.com/sponsors/plutoprint

License
-------

PlutoPrint is licensed under the `MIT License <https://github.com/plutoprint/plutoprint/blob/main/LICENSE>`_, allowing for both personal and commercial use.

.. |build| image:: https://img.shields.io/github/actions/workflow/status/plutoprint/plutoprint/main.yml
   :target: https://github.com/plutoprint/plutoprint/actions
.. |docs| image:: https://img.shields.io/readthedocs/plutoprint
   :target: https://plutoprint.readthedocs.io
.. |license| image:: https://img.shields.io/pypi/l/plutoprint
   :target: https://github.com/plutoprint/plutoprint/blob/main/LICENSE
.. |downloads| image:: https://img.shields.io/pypi/dm/plutoprint
.. |pypi| image:: https://img.shields.io/pypi/v/plutoprint
   :target: https://pypi.org/project/plutoprint
.. |pyver| image:: https://img.shields.io/pypi/pyversions/plutoprint
