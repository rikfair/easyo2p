Datatypes
=========

Column datatypes between Oracle and PostgreSQL vary slightly,
although they can, mostly, be mapped from one to the other.

.. list-table:: Datatype Mapping
   :widths: 50 50
   :header-rows: 1

   * - Oracle
     - PostgreSQL

   * - BINARY_DOUBLE
     - FLOAT(8)
     
   * - BINARY_FLOAT
     - FLOAT(4)
     
   * - FLOAT
     - FLOAT(8)

   * - NUMBER(precision,scale)
     - NUMERIC(precision,scale)

   * - NUMBER name ends "_ID"
     - INTEGER

   * - NUMBER(precision < 5)
     - SMALLINT

   * - NUMBER(precision > 9)
     - BIGINT

   * - NUMBER(precision)
     - INTEGER

   * - NUMBER
     - NUMERIC

   * - (N)CHAR, (N)VARCHAR2
     - VARCHAR

   * - DATE
     - TIMESTAMP(0)

   * - (N)CLOB
     - TEXT

   * - BLOB
     - BYTEA

.. important::
    The mappings are checked in order, top to bottom,
    so any that Oracle column conditions that meet more than one criteria,
    will be mapped to the first map found.

The mapping process will map an Oracle datatype to the most efficient PostgreSQL
datatype it can, So ``NUMBER(2,0)`` will map to ``SMALLINT`` rather than ``NUMERIC(2,0)``.
On its own, this could change the logic of the application,
as the migrated column could accept numbers larger than 99.
So a check constraint is also created to ensure values are within the Oracle boundaries.
If undesired, the check constraints can be removed in the post ETL stage.

Instances where the mappings need to be overridden,
such as when an Oracle foreign key links a NUMBER without precision to a NUMBER with precision,
causing a Datatype Mismatch error, the ``COLUMN_DATATYPES`` parameter can be used.
This expects a list of ``<table_name.column_name> <PostgreSQL Datatype>``.
Note the values are space separated.
