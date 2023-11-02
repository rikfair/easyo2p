Tutorial 2: Create ETL Files
============================

Now the scott schema has been created,
ETL files can be built to create the tables and insert the data into PostgreSQL.

#. Use the ``filesonly.py`` python script in the ``tutorial`` directory.

#. Create a path to store the created files and modify the ``filesonly.py`` constant ``ETL_PATH``.

    The ``filesonly.py`` script will create a new directory for each run.
    This directory name will be based on the date and time of the run.
    These will all be in a further sub-directory of the ``ETL_PATH`` directory, called ``exports``.

#. Set Oracle Instant Client location.

    Locate your local Oracle Instant Client location
    and modify the ``ORACLE_INSTANT_CLIENT`` constant in the ``filesonly.py`` script.

#. Modify the connection constants.

    .. code-block:: python3

      ...
      ORAUSER = 'scott'
      ORAPASS = 'tiger'
      ORAPORT = '1521'
      ORAHOST = '<specific host>'
      ORADBASE = '<specific database>'
      ...

#. Run the ETL files on PostgreSQL.

    You can now create the scott tables on PostgreSQL.
    Using ``psql``, run the newly created ``_run_.sql`` file.
    The command to run can be found as a comment at the top of the ``_run_.sql`` file.

    .. important::
      psql needs to be set to the same character set as ``easyo2p``,
      which by default is UTF-8. To set psql to UTF-8, set the ``PGCLIENTENCODING``
      environment variable before running psql.

      .. code-block::

        SET PGCLIENTENCODING=utf-8

    .. code-block::

      psql -d easyo2p_db -U easyo2p_user

      easyo2p_db=> \i 'C:\Temp\EasyO2P\filesonly\<datetime>\_run_.sql'

    .. note::
      The run script drops the scott schema before recreating it,
      so it can be run after any of the following steps where the files are created.


#. Run the script.

    Run the ``filesonly.py`` script. When complete,
    four files should be created in the ``<ETL_PATH>/exports/<datetime>/etl`` directory.
    One for each of the table create statements, and another one for the constraints and indexes.

#. Turn on the data parameter.

    .. code-block:: python3

      ...
      parameters = {
          easyo2p.ETL_DATA: True,
          ...

#. Run the script again.

    Run the ``filesonly.py`` script. When complete,
    a new dated directory should contain six migration files, four as before,
    and two new files containing data for each table,
    along with the run and log files.

#. Migrate only selected tables.

    By default, all tables in the schema will be migrated.
    To select specific tables, include the ``TABLES`` parameter.
    This expects a list of table names.

    To migrate only the EMP table modify the parameters declaration:

    .. code-block:: python3

      ..
      parameters = {
          easyo2p.TABLES: ['EMP'],
          ...

    When the script is run now only the EMP table is migrated.


**ETL Files**

The migration process creates up to three files for each table.

Files suffixed ``.3.sql`` contain the table create statements.
These should all be run first.

Files suffixed ``.4.sql`` contain the data insert statements.
These should always be all run next, before the constraints.

Files suffixed ``.5.sql`` contain the constraint, index and trigger statements.
These should always be all run afterwards,
to ensure all referencing tables are created and not to affect the data migration.

    .. note::

        Files suffixed ``.1.sql`` are custom pre-build files, such as PL/pgSQL objects,
        to be run first.
        The file suffixed ``.2.sql`` is ``sequences.2.sql``,
        this contains the create sequence statements.
        Files suffixed ``.6.sql`` are custom post-build files, such as for granting permissions,
        to be run last of all. These will be covered in more detail in a later step.

We should now understand how to use ``easyo2p`` to create ETL scripts
that can build tables and insert data.
