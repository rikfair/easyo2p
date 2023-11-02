Tutorial 5:  Datatypes
======================

The Oracle column datatypes need to be mapped to PostgreSQL datatypes.
The mappings themselves are documented in the ``Datatypes`` API page.

The ``salgrade1`` table has been mapped to:

.. code-block:: sql

    CREATE TABLE IF NOT EXISTS scott.salgrade1
    (
        salgrade1_id integer NOT NULL,
        grade smallint,
        losal bigint,
        hisal numeric,
        CONSTRAINT pk_salgrade1 PRIMARY KEY (salgrade1_id),
        CONSTRAINT salgrade1_grade_check CHECK (grade < 100)
    )
    TABLESPACE pg_default;


* The primary key ``salgrade1_id`` has been mapped to ``INTEGER``.
* The ``NUMBER(2,0)`` column ``grade`` has been mapped to ``SMALLINT``, with a check constraint.
* The ``losal`` column is a ``FLOAT``, so maps to ``FLOAT``.
* And the ``hisal`` column is a ``NUMBER``, so maps to ``NUMERIC``.

#. Standardise the ``losal`` and ``hisal`` datatypes.

    Using the ``base.py`` tutorial script, add the ``COLUMN_DATATYPES`` parameter.

    .. code-block:: python3

        ...
        parameters = {
            easyo2p.COLUMN_DATATYPES: [
                'SALGRADE1.LOSAL BIGINT',
                'SALGRADE1.HISAL BIGINT'
            ],
            ...

#. Run the script.

    Run the ``base.py`` script.
    Once complete the ``losal`` and ``hisal`` columns should have consistent datatypes.

    .. code-block:: sql

        CREATE TABLE scott.SALGRADE1
        ( SALGRADE1_ID           INTEGER NOT NULL
        , GRADE                  SMALLINT CHECK (GRADE < 100)
        , LOSAL                  BIGINT
        , HISAL                  BIGINT
        ) TABLESPACE pg_default
        ;

.. note::
    as PostgreSQL string columns are defined by the number of characters,
    Consider using the ``COLUMN_DATATYPES`` parameter
    if any Oracle character columns, that are defined as ``BYTE``,
    need their length adjusted.
