Parameters
==========

The following parameters control how ``easyo2p`` operates and are crucial for a successful migration.
They are set when declaring for the ``O2P`` class
and several may be additional set using the ``O2P.set_parameter`` method.
See the API documentation page for a list of which ones.

Examples of how the parameters can be used, good practices and limitations,
are covered in the tutorial pages.


.. list-table:: Parameters
   :widths: 20 10 70
   :header-rows: 1

   * - Parameter
     - Type
     - Description

   * - column_datatypes
     - list
     - An override of the datatype mapping. A list of column datatype pairs, space separated.
       EG. ``['TABLE_NAME.COLUMN_NAME VARCHAR2(256)']``

   * - column_reorder
     - dict
     - Reorders the columns for the specified tables.
       Any columns not in the list will be included after those in the list.
       EG. ``{'TABLE_NAME': ['COLUMN_NAME1', 'COLUMN_NAME2']}``

   * - console
     - bool
     - Writes log output to the console when true. Default True.

   * - drop_schema
     - bool
     - Drops the PostgreSQL schema before migrating objects and data. Default True.

   * - encoding
     - str
     - The encoding scheme to be applied. Default ``utf-8-sig``.

   * - etl_comments
     - bool
     - Whether to include table and column comments in the migration. Default True.

   * - etl_constraints
     - bool
     - Whether to include constraints in the migration. Default True.

   * - etl_data
     - bool
     - Whether to include data in the migration. Default True.

   * - etl_files
     - bool
     - Whether to create a set of migration script files. Default True.

   * - etl_migrate
     - bool
     - Whether to migrate directly to PostgreSQL. Default True.

   * - etl_triggers
     - bool
     - Whether to include triggers in the migration. Default False.

   * - exclude
     - list
     - A list of objects to exclude from the migration.
       This overrides any provided in the object specific parameters.
       Each element is expected to contain the object type and the object name.
       EG: ``['TRIGGER TRIGGER_NAME1', 'COLUMN TABLE_NAME.COLUMN_NAME']``.
       Valid object types that can be excluded are:

       * COLUMN
       * CONSTRAINT
       * INDEX
       * SEQUENCE
       * TABLE
       * TRIGGER

   * - insert_rows
     - int
     - The number of rows to include in each insert statement. Default 10,000.

   * - oracle_conn
     - str
     - The oracle connection string. EG: ``<username>/<password>@<host>:<port>/<database>``.
       This parameter must be provided.

   * - oracle_instant_client
     - str
     - The execute path to the Oracle Instant Client. This parameter must be provided.

   * - postgres_conn
     - str/list
     - The PostgreSQL connection string. EG:
       ``user='<username>' password='<password>' dbname='<database>' host='<host>' port='<port>'``.
       The parameter must be provided if migrating directly to PostgreSQL.

       To migrate an Oracle Database to multiple PostgreSQL databases,
       a list of connection strings can be provided.

   * - postgres_schema
     - str
     - The schema to use in PostgreSQL. If it does not exist, it will be created. Default 'O2P'.

   * - rename
     - list
     - A list of objects to rename during the migration.
       Each element is expected to contain the object type, existing name in Oracle,
       and the migrated PostgreSQL name.
       EG: ``['COLUMN LIMIT BONUS_LIMIT', 'INDEX EMP_I EMP_IDX']``.
       See the exclude parameter for a list valid object types.

   * - sequences
     - list
     - A list of all the sequences to include in the migration.
       When not provided, all sequences will be included.

   * - tables
     - list
     - A list of all tables to include in the migration.
       When not provided, all sequences will be included.

   * - tablespace_map
     - list
     - Use only when tablespaces are to be specified.
       A list of elements mapping Oracle objects to PostgreSQL tablespace.
       Each element expects an object name, either ``TABLE`` or ``INDEX``,
       along with the tablespace name, space separated. Default {}.

   * - target_path
     - str
     - The path for outputting the scripts and log file. This parameter must be provided.

   * - triggers
     - list
     - A list of all triggers to include in the migration.
       When not provided, all sequences will be included.

.. note::
    The easyo2p package has a constant for each parameter for assurance and readability.
    These are all uppercase versions of the parameter name.
    EG: ``etl.set_parameter(easyo2p.ETL_DATA, False)``
