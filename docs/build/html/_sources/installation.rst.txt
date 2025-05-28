Installation
============

Requirements
-----------

* Python 3.10 or higher
* httpx >= 0.24
* pydantic >= 2.0

Basic Installation
----------------

You can install aiopromql using pip:

.. code-block:: bash

    pip install aiopromql

Development Installation
----------------------

To install aiopromql with development dependencies:

.. code-block:: bash

    pip install -e .[dev]

Or using make:

.. code-block:: bash

    make install

This will install additional development tools including:

* ruff (linting)
* pytest (testing)
* hatch (build system)
* pytest-asyncio (async testing)
* pytest-cov (coverage)
* sphinx (documentation) 