Tutorial 8: Queries
===================

So far we've only given ``easyo2p`` static parameters but migration environments,
especially those that are in production, change during testing.

Populating parameters with queries provides an up to date view of the Oracle database.
Here we give just a few examples of how they can be used,
with the aim of providing inspiration for imagination to solve migration specific issues.

.. note::
    The following examples assume you've become familiar with the ``base.py`` tutorial script by now,
    able to set the connection parameters, and have some Python coding knowledge.


#. Build the sequences list with a query.

    In this example we use queries to convert an Oracle schema that uses sequences to populate
    columns using a trigger, to PostgreSQL columns with *default nextval* clauses.

    The ``queries.py`` tutorial script expands on the ``base.py`` script with two new functions,
    ``_get_table_sequences`` and ``_get_sequence_column``.
    Together these find the relationships between sequences and columns.
    This is a specific scenario where we assume triggers that reference sequences are suffixed
    ``_SEQTRG`` but this is easily adaptable to fit many other scenarios.

    As with the previous scripts, enter your specific connection details before running.

    Once run, the PostgreSQL schema should show the ``salgrade1`` table with column ``salgrade1_id``
    having the ``DEFAULT NEXTVAL('SALGRADE1_SEQ')`` clause.


#. Dynamic exclude parameter.

    The ``EXCLUDE`` parameter expects a list of objects to exclude.
    Here we exclude any table or column where its comment starts with ``DEPRECATED``.

    Add comments to the Oracle scott schema to deprecate some objects.

    .. code-block:: sql

        COMMENT ON TABLE bonus IS 'DEPRECATED This table is not to be migrated';
        COMMENT ON COLUMN emp.hiredate IS 'DEPRECATED This column is not to be migrated';

    Then, using the ``queries.py`` tutorial script, insert the following code.

    .. code-block:: python3

        query = (
            "SELECT 'TABLE ' || table_name exclude"
            "  FROM user_tab_comments "
            " WHERE comments LIKE 'DEPRECATED%' "
            " UNION ALL "
            "SELECT 'COLUMN '|| table_name || '.' || column_name"
            "  FROM user_col_comments "
            " WHERE comments LIKE 'DEPRECATED%' "
        )
        exclude = [i[0] for i in etl.oracle_query(query)]
        etl.set_parameter(easyo2p.EXCLUDE, exclude)

    Run the script, once complete the migration will have excluded the ``bonus`` table
    and the ``emp.hiredate`` column.


#. An alternative to populating parameters with queries.

    Another way to populate parameters is with files,
    which can create easier to read scripts and options to produce parameters using other methods.

    Locate the ``exclude.txt`` script in the ``tutorial`` directory
    and place it in the ``ETL_PATH`` directory.

    Using the ``queries.py`` script, replace the code snippet from step 2 with:

    .. code-block:: python3

        exclude = etl.file_read_to_string(os.path.join(ETL_PATH, 'exclude.txt')).split('\n')
        etl.set_parameter(easyo2p.EXCLUDE, exclude)

    Run the script, once complete the migration will have excluded the ``salgrade1`` table
    and the ``bonus.comm`` column.


#. Combine files and queries.

    More complex queries may not suit being written within code.
    Placing queries in files could be an option to make code simpler and more readable.

    Locate the ``exclude.sql`` script in the ``tutorial`` directory
    and place it in the ``ETL_PATH`` directory.

    Using the ``queries.py`` script, replace the code snippet from step 3 with:

    .. code-block:: python3

        exclude_sql = etl.file_read_to_string(os.path.join(ETL_PATH, 'exclude.sql'))
        exclude = [i[0] for i in etl.oracle_query(exclude_sql)]
        etl.set_parameter(easyo2p.EXCLUDE, exclude)

    The scott schema should again be migrated without the deprecated tables or columns.


#. Using views as pseudo tables.

    Another use of a query is as a view. ``easyo2p`` will build a migrate a view,
    as if it were a table, if it's in the ``TABLES`` parameter.

    To do this, first create an emp dept view.

    .. code-block:: sql

        CREATE VIEW employee AS
        SELECT e.empno,
               e.ename,
               d.dname
          FROM emp e,
               dept d
         WHERE e.deptno = d.deptno;

    Then include the view in the include parameter.
    As we are specifying the parameter, we don't migrate all tables by default.

    Using the ``queries.py`` script, replace the code snippet from step 4 with:

    .. code-block:: python3

        etl.set_parameter(easyo2p.TABLES, ['EMPLOYEE'])

    .. note::
      We are using the set_parameter method here for consistency,
      but here the TABLES parameter would be better set in the class declaration.

    Run the script. Once complete an employee table should exist in PostgreSQL,
    with data from the ``emp`` and ``dept`` views

    As views don't have a tablespace it will be stored in the default table tablespace.
    Use the ``TABLESPACE_MAP`` parameter to specify the tablespace if required.

    Any constraints or indexes can be specified using scripts after the ``do_etl`` stage,
    see the next step, PL/SQL, for details on how this is configured.
