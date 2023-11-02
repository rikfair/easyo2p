Tutorial 3: Migrate Directly to PostgreSQL
==========================================

Now we know how to create ETL files,
the next step is to migrate the schema from Oracle directly to PostgreSQL.

#. Use the ``base.py`` python script in the ``tutorial`` folder.

#. Modify the constant values as in step 2.

    The ``ETL_FILES``, ``ORACLE_INSTANT_CLIENT`` and Oracle connection constants
    should all be given the same values as in Tutorial step 2.

#. Modify the PostgreSQL connection constants, adding the specific server host details.

    .. code-block:: python3

      ...
      PGSSCHEMA = 'scott'
      PGSDBASE = 'easyo2p_db'
      PGSUSER = 'easyo2p_user'
      PGSPASS = 'easyo2p_pwd'
      PGSPORT = '5432'
      PGSHOST = '<specific host>'
      ...

#. Run the script.

    Run the script in the same as before.
    This time the scott schema will be created in PostgreSQL as well as the ETL scripts.

    .. note::

        If you wished to prevent the scripts being created, add the ``ETL_FILES``
        element to the parameters dictionary in the modified ``base.py`` script.

        .. code-block:: python3

            ...
            parameters = {
                easyo2p.ETL_FILES: False,
                ...

We should now understand how to use ``easyo2p`` to migrate an Oracle schema to PostgreSQL,
either directly or using ETL scripts.
