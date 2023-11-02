PL/SQL to PL/pgSQL
==================

Whilst this application's focus is on moving the data,
it does try to cover some basic PL/SQL conversion to PL/pgSQL,
although this is by no means comprehensive.

Or to be more exact, it replicates a few common Oracle function names,
so existing Oracle function calls continue to work in PL/pgSQL,
limiting the amount of further code modification.

.. important::

    This may cover database conversions with limited PL/SQL usage.
    But where PL/SQL has been used more extensively, consider a more specific tool such as orafce

There are two prongs to the migration of PL/SQL to PL/pgSQL.

Firstly, there are straight forward string replacements.
Whether this quick and dirty method is suitable for a specific migration depends on each application,
as replacements may be made in undesirable places, so checking the resulting code is essential.

.. list-table:: Strings replaced by default
   :widths: 20 20 60
   :header-rows: 1

   * - Oracle
     - PostgreSQL
     - Purpose
   * - \\t
     - "  "
     - Tab replaced by two spaces
   * - :OLD.
     - OLD.
     - Colon removed from OLD for trigger syntax
   * - :NEW.
     - NEW
     - Colon removed from NEW for trigger syntax
   * - INSERTING
     - TG_OP = 'INSERT'
     - Trigger syntax for INSERTING
   * - UPDATING
     - TG_OP = 'UPDATE'
     - Trigger syntax for UPDATING
   * - DELETING
     - TG_OP = 'DELETE'
     - Trigger syntax for DELETING
   * -  NUMBER
     -  NUMERIC
     - Number datatype (prefixed by a space)
   * -  PLS_INTEGER
     -  INTEGER
     - Integer datatype (prefixed by a space)
   * - SQL%ROWCOUNT
     - sql_rowcount()
     - To make use of the wrapper function (see below)
   * - SYS.DUAL
     - DUAL
     - To make use of the schema owned view (see below)

Secondly, scripts can be run to create objects to mimic Oracle functionality or syntax.
The following scripts, and any additional that you may wish to create to expand the replicated functions,
need to be added ``prebuild`` directory.

DUAL
----

The SYS.DUAL table does not exist in PostgreSQL.
The FROM clause is optional, so no dummy table is required to complete a SELECT statement.
The ``dual.sql`` script creates a view to mimic Oracle's DUAL.
This view is created in the target schema so references to ``DUAL`` will compile.
By default, ``SYS.DUAL`` will be converted to just ``DUAL`` during the migration.

INSTR
-----

In PostgreSQL the equivalent of Oracle's ``INSTR``, is ``POSITION``.
The ``instr.sql`` script creates a wrapper for the ``POSITION`` function,
to keep code compiling.

LAST_DAY
--------

Oracle's ``LAST_DAY`` function returns the last day for the month of a given date.
The ``last_day.sql`` script creates a function to replicate this in PostgreSQL.

NVL
---

Oracle and PostgreSQL share the standard ``COALESCE`` function,
but to facilitate the use of the older ``NVL`` function, the scripts ``nvl_date.sql``,
``nvl_numeric.sql`` and ``nvl_varchar.sql`` cater for some scenarios.


RAISE_APPLICATION_ERROR
-----------------------

The syntax for raising an error within PL/SQL and PL/pgSQL differs ever so slightly,
but enough to cause compilation errors. The ``raise_application_error`` script creates a wrapper,
so existing ``RAISE_APPLICATION_ERROR`` calls will continue to function.

SQL_ROWCOUNT
------------

Wrapper for the PL/pgSQL equivalent of the Oracle ``SQL%ROWCOUNT`` functionality.
By default, ``SQL%ROWCOUNT`` will be converted to ``sql_rowcount()`` during the migration.

TO_CHAR, TO_DATE, TO_NUMBER
---------------------------

Oracle and PostgreSQL share the standard `CAST` function,
but the scripts ``to_char.sql``, ``to_date.sql``, ``to_number_<x>.sql``
facilitates the use of the older ``TO_XXX`` functions.

TRUNC(DATE)
-----------

Oracle ``TRUNC`` function when used with a date, sets the time element to midnight.
The ``trunc_date.sql`` script replicates that functionality.
