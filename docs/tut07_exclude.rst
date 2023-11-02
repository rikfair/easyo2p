Tutorial 6: Excluding Objects
=============================

Selecting which objects to migrate can be achieved in two ways.
Either, listing the objects that are required in the appropriate parameter,
or adding the undesired objects to the ``EXCLUDE`` parameter.
Which method to use, or combination of both, depends on each migration's requirement.

.. note::
    The ``EXCLUDE`` list overrides the specific include object lists.

#. Add the ``EXCLUDE`` parameter to the script.

    The ``EXCLUDE`` parameter expects a list of two space separated values:

    #. The object type, TABLE, COLUMN, CONSTRAINT, INDEX, SEQUENCE, or TRIGGER.

    #. The object name in Oracle, use TABLE_NAME.COLUMN_NAME syntax for columns.

    Replace the parameters declaration in ``base.py`` with:

    .. code-block:: python3

      ...
      parameters = {
          easyo2p.EXCLUDE: [
              'TABLE SALGRADE1',
              'COLUMN BONUS.LIMIT',
              'CONSTRAINT PK_EMP',
              'INDEX EMP_ENAME_IDX',
              'SEQUENCE SALGRADE1_SEQ',
          ],
          # Connection info
          easyo2p.ORACLE_INSTANT_CLIENT: ORACLE_INSTANT_CLIENT,
          easyo2p.ORACLE_CONN: f"{ORAUSER}/{ORAPASS}@{ORAHOST}:{ORAPORT}/{ORADBASE}",
          easyo2p.POSTGRES_CONN: (
              f"dbname='{PGSDBASE}' user='{PGSUSER}' host='{PGSHOST}' "
              f"password='{PGSPASS}' port='{PGSPORT}'"
          ),
          easyo2p.POSTGRES_SCHEMA: PGSSCHEMA,
          easyo2p.TARGET_PATH: os.path.join(ETL_PATH, 'exports', now)
      }
      ...

#. Run the script.

    Run the ``base.py`` script.
    Once complete the migration should now exclude the objects listed in the ``EXCLUDE`` parameter.


    .. important::
        Excluding tables or columns that are referenced by foreign key constraints
        will result in an error, as referenced columns are not checked.

        These constraints also need to be included in the ``EXCLUDE`` parameter list.
