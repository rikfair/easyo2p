Tutorial 9: PL/SQL
==================

Before we move on to triggers, we need to acknowledge that there are many tools
to convert Oracle code to PostgreSQL code but ``easyo2p`` is not a
comprehensive tool to for this.

Instead ``easyo2p`` concentrates on data and objects required to support the data.
Triggers often come into this category, so ``easyo2p`` has some ability to convert simple triggers.

Having said that, the ability to run scripts before and after the ETL step,
offers the option to run manually converted PL/SQL program units as part of the migration process.

The ``plsql`` directory contains several scripts to replicate Oracle functionality in PostgreSQL.
These are in two sub-directories, ``pre_etl`` and ``post_etl``,
indicating the point at which they should be executed.
The ``easyo2p`` approach is to use these wrapper functions to enable triggers to compile and run,
rather than convert the Oracle code to a PostgreSQL equivalent.
Each function contains a description of what it is,
select which, if any, or add scripts in these directories if required.


#. Make a local copy of the plsql directories.

    Copy the ``pre_etl`` and ``post_etl`` sub-directories of the ``plsql`` directory
    to the ``ETL_FILE`` directory.


#. Use the ``plsql.py`` python script in the ``tutorial`` folder.

    The ``plsql.py`` tutorial script expands on the ``base.py`` script,
    with calls to the ``postgresql_file`` method to run files from the ``pre_etl``
    and the ``post_etl`` directories.

    As with the previous scripts, enter your specific connection details before running.
    This is based on the ``base.py`` script. Set the parameters as with step 2.

    .. note::
        If the order of scripts is important due to dependencies,
        the sequence of the scripts can be manipulated to insure the processing order,
        either by filename convention, multiple directories, or individual processing.

#. Run the script.

    Run the ``plsql.py`` script, the PLpg/SQL script should be run and objects created
    and permissions granted.


#. Check the ETL files.

    The ``ETL_FILES`` sub-directory for this run should now contain a copy of each script
    run using the ``postgresql_file`` method.
    Any run before the ``do_etl`` method are suffixed ``.1.sql`` and those after ``.6.sql``.

    Each PLpg/SQL file also has a number prefixed, which indicates the order in which they are run,
    so the run script replays them in the same order.

.. note::

  When creating objects, ``easyo2p`` requires the schema name.
  At runtime occurances of the string ``%%schema%%`` found in scripts,
  will be replaced with the ``POSTGRES_SCHEMA`` parameter value,
  to allow for dynamic schema naming.
