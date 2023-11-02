easyo2p
=======
**Oracle to PostgreSQL Migration with Python**

``easyo2p`` is a Python package to migrate an Oracle database schema to PostgreSQL.
Containing functionality to connect to both source and target databases,
``easyo2p`` eases customised migrations using its functionality within the Python environment.

Requirements
------------

``easyo2p`` is written and tested on Python 3.10,
using cx_Oracle and psycopg2 database connections modules.

The package can be found on `GitHub <https://github.com/rikfair/easyo2p>`_
and `PyPI <https://pypi.org/project/easyo2p/>`_,
so naturally it can be installed with `pip`

.. code-block::

   pip install easyo2p

It has been tested with various Oracle versions from version 12c,
and PostgreSQL from 14, but is expected to work with a

Audience
--------

``easyo2p`` is for you if:

* You want to copy a schema, or multiple schemas, in Oracle to PostgreSQL.
* You need no or little automated conversion of PL/SQL functions, procedures or packages.
* You are familiar enough with Python to add any required customisations.

Operation
---------

The package can connect to both the Oracle and PostgreSQL servers.
From a specified schema, it will create the objects in PostgreSQL and migrate the data.
``easyo2p`` also has an option to create text files,
so that the migration can be backed-up or rerun later.

To ease continuity between Oracle and PostgreSQL development,
and to allow our PL/SQL code to run in both Oracle and PostgreSQL,
some additional objects are created to mimic Oracle functionality in PostgreSQL.

Getting Started
---------------

The tutorial covers examples of the ``easyo2p`` functionality,
so that it can then be applied for specific migrations.

Licence
-------

This software is released under the MIT licence