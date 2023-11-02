Tutorial 7: Tablespaces
=======================

So far the tutorial has only used default tablespaces,
with Oracle tables and indexes being created in scott's default tablespace
and the migrated objects being created in the default PostgreSQL tablespace.

If that is sufficient, you can move on to the next step,
but if specifying tablespaces is important
there is the option of using the ``TABLESPACE_MAP`` parameter.

.. note::
    PostgreSQL tablespaces are unlike Oracle tablespaces,
    in that other than specifying which disk the data is to use,
    there is no *"non-advanced"* reason to use them.
    Multiple tablespaces on the same disk are largely pointless and may lead to backup complexities.


The parameter expects a list, with two space separated values.

    #. Either the object type, tablespace name, or tablespace name with object name.
    #. The new PostgreSQL tablespace name.

For example:

.. code-block:: python3

    ...
    parameters = {
        # Tablespace mapping
        easyo2p.TABLESPACE_MAP: [
            'EMP pgtbs_emp',
            'PK_EMP pgtbs_emp',
            'INDEX.EMP_ENAME_IDX pgtbs_emp',
            'ORATBS_TABLES pgtbs_tables1',
            'TABLE pgtbs_tables2',
            'INDEX pgtbs_indexes1',
        ],
    ...

The ``EMP`` and ``PK_EMP`` objects will be created in the ``pgtbs_emp`` tablespace in PostgreSQL.

Using ``object_type.object_name`` syntax,
it then specifies the index ``emp_ename_idx``
to be created in the PostgreSQL tablespace ``pgtbs_emp``.
This notation only needs to be used if tables and indexes exist with the same object name.

Then, any objects in the ``ORATBS_TABLES`` tablespace,
will be created in the ``pgtbs_tables1`` in PostgreSQL.

Then, any other tables, in any Oracle tablespace,
will be created in the ``pgtbs_tables2`` PostgreSQL tablespace.

The, any other indexes, in any Oracle tablespace,
will be created in the ``pgtbs_indexes1`` PostgreSQL tablespace.

.. note::

    The following steps are not required later in the tutorial,
    so can be skipped if they're not relevant to your migration.

#. Create tablespaces on PostgreSQL.

    For this step we need to create three tablespaces on PostgreSQL.

    In ``psql`` create the following tablespaces using a privileged user account.

    .. code-block:: sql

        CREATE TABLESPACE pgtbs_emp OWNER easyo2p_user LOCATION '<path>\pgtbs_emp';
        CREATE TABLESPACE pgtbs_tables1 OWNER easyo2p_user LOCATION '<path>\pgtbs_tables1';
        CREATE TABLESPACE pgtbs_indexes1 OWNER easyo2p_user LOCATION '<path>\pgtbs_indexes1';

#. Modify the script connection details.

    Using the ``tablespace.py`` script in the ``tutorial`` directory,
    enter the connection details, as previously done with ``base.py``.

#. Modify the tablespace map.

    The script assumes the scott schema tables created were created in the ``DEFAULT`` tablespace.
    Adjust the following values if necessary.

    .. code-block:: python3

        easyo2p.TABLESPACE_MAP: [
            'EMP pgtbs_emp',
            'PK_EMP pgtbs_emp',
            'INDEX.EMP_ENAME_IDX pgtbs_emp',
            'DEFAULT pgtbs_tables1',
            'TABLE pg_default',
            'INDEX pgtbs_indexes1',
        ],

#. Run the script.

    Run the ``tablespace.py`` script. When complete the tables will be in the expected tablespaces.

