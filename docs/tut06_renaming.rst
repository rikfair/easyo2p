Tutorial 6:  Renaming Objects
=============================

There are often reasons to rename objects during migration.
Such as when using a PostgreSQL reserved word in Oracle or just to standardise a naming convention.

The ``RENAME`` parameter will allow an object to be renamed as it migrates.

#. Create a new table for scott

    Let's create scott a new table, ``bonus``,
    this has a column that uses a PostgreSQL reserved word, ``limit``.

    Create the following table in the Oracle scott schema:

    .. code-block:: sql

        CREATE TABLE bonus
        ( ename       VARCHAR2(10),
          job         VARCHAR2(9),
          sal         NUMBER,
          comm        NUMBER,
          limit       NUMBER
        );

        COMMENT ON COLUMN bonus.limit IS 'Rename limit to bonus_limit';

        INSERT INTO bonus VALUES ('SMITH','CLERK',10,20,30);
        COMMIT;

#. Run the script.

    Run the ``base.py`` script from the previous step,
    which should produce the following error,
    as the ``limit`` column name is a reserved word in PostgreSQL but not in Oracle.

    .. code-block:: python3

      psycopg2.errors.SyntaxError: syntax error at or near "LIMIT"

#. Include the ``RENAME`` parameter.

    The ``RENAME`` parameter expects a list of three space separated values:

    #. The object type, TABLE, COLUMN, CONSTRAINT, INDEX, SEQUENCE, or TRIGGER.

    #. The object name in Oracle, use TABLE_NAME.COLUMN_NAME syntax for columns.

    #. The object name to create in PostgreSQL.

    Add the following to the ``parameters`` declaration in ``base.py``

    .. code-block:: python3

      ...
      parameters = {
          easyo2p.RENAME: ['COLUMN BONUS.LIMIT BONUS_LIMIT'],
          ...

#. Run the script.

    Run the ``base.py`` script again.
    Once complete the migration should now include the ``bonus`` table
    with the column ``bonus_limit``.

#. A few more examples.

  Again, modify the ``base.py`` script to rename some more objects.

  .. code-block:: python3

    ...
    parameters = {
        easyo2p.RENAME: [
            'COLUMN BONUS.LIMIT BONUS_LIMIT',
            'COLUMN EMP.SAL SALARY',
            'COLUMN SALGRADE1.SALGRADE1_ID SALARY_GRADE_ID',
            'CONSTRAINT PK_EMP EMPLOYEES_PK',
            'CONSTRAINT PK_DEPT DEPARTMENTS_PK',
            'CONSTRAINT FK_DEPTNO DEPTNO_FK',
            'INDEX EMP_ENAME_IDX ENAME_INDEX',
            'SEQUENCE SALGRADE1_SEQ SALARY_GRADE_SEQ',
            'TABLE DEPT DEPARTMENTS',
            'TABLE EMP EMPLOYEES',
            'TABLE SALGRADE1 SALARY_GRADE',
        ],
        ...

  Several name changes should now be visible in PostgreSQL.
