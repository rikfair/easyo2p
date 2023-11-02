Tutorial 10: Triggers
=====================

As mentioned in the previous step, ``easyo2p`` has some, but not complete,
support for trigger migration.

.. note::
    Any triggers that are not possible to migrate automatically
    can always be manually translated and processed as a post ETL script.


#. Create a trigger for scott.

    Create a trigger in the Oracle scott schema.

    .. code-block:: sql

        CREATE TRIGGER dept_loc_upper_trg
        BEFORE INSERT OR UPDATE OF loc ON dept
        FOR EACH ROW
        BEGIN
          :NEW.loc := UPPER(:NEW.loc);
        END;
        /


#. Run the script.

    Using the ``plsql.py`` script from the previous step,
    add the following to the parameter declaration.

    .. code-block::

      ...
      parameters = {
        easyo2p.TRIGGERS: ['DEPT_LOC_UPPER_TRG'],
        ...

    Run the script. Once complete a trigger function and trigger will be created.
    As can be seen below some transformations have taken place.

    .. code-block:: plpgsql

        CREATE FUNCTION DEPT_LOC_UPPER_TRG_TF()
        RETURNS TRIGGER
        LANGUAGE PLPGSQL
        AS
        $$
        BEGIN
          NEW.loc := UPPER(NEW.loc);
          RETURN NEW;
        END;
        $$;

        CREATE TRIGGER DEPT_LOC_UPPER_TRG
        BEFORE INSERT OR UPDATE ON DEPT FOR EACH ROW
        EXECUTE PROCEDURE DEPT_LOC_UPPER_TRG_TF();

    * Each Oracle trigger creates two objects in PostgreSQL,
      the trigger function and the table trigger.

    * The NEW and OLD references have no colon prefixes.

    * The trigger function returns the NEW values.

    * ``easyo2p`` gives trigger functions a ``_TF`` suffix.

    These changes are made mainly using string replacement, so can be temperamental.
    If ``easyo2p`` is unable to transform a trigger,
    it can be rewritten manually and included in the post ETL scripts,
    with the trigger name being included in the ETL exclude list.


#. Create a trigger referencing Oracle only functions.

    Create a trigger in the Oracle scott schema.

    .. code-block:: sql

      CREATE TRIGGER dept_x2_trg
      BEFORE INSERT OR UPDATE OF dname ON dept
      FOR EACH ROW
      BEGIN
        IF INSTR(:NEW.dname, 'X') = 2 THEN
          RAISE_APPLICATION_ERROR(-20101, 'X not allowed as second character');
        END IF;
      END;
      /

    This trigger will cause issues with INSTR and RAISE_APPLICATION_ERROR.


#. Run the script.

    Using the ``plsql.py`` script from the previous step,
    add the following to the parameter declaration.

    .. code-block:: python3

      ...
      parameters = {
        easyo2p.TRIGGERS: ['DEPT_LOC_UPPER_TRG', 'DEPT_X2_TRG'],
        ...

    A replacement function for ``INSTR`` and a
    ``RAISE_APPLICATION_ERROR`` alternative procedure are included in the pre ETL directory.

    As ``RAISE_APPLICATION_ERROR`` is a procedure,
    we need to include some transformation information.

    Add the following line to the ``plsql.py`` script for this, just before the ``do_etl`` call.

    .. code-block:: python3

      ...
      etl.set_pls2pgs({'RAISE_APPLICATION_ERROR': 'CALL RAISE_APPLICATION_ERROR'})
      ...

    Run the script. Once complete the trigger function and trigger will be created.
    As can be seen below some transformations have taken place.


**And that's all there is to it.**

The tutorial and the functionality of ``easyo2p`` has now been covered...

Remember, the premise of ``easyo2p`` is to migrate an Oracle schema to PostgreSQL as simply as possible.
All applications have their quirks, which are likely to require manual intervention.
``easyo2p`` aims to cover the vast majority of the migration and aid with the remainder, those quirks.

Make use of the power of Python and ``easyo2p``'s database connections to populate parameters
dynamically whenever needed. Use the tutorial examples as a starting point and add whatever you need.
Migrate multiple schemas using multiple ``O2P`` classes,
even bring schemas together or tidy the structure whilst you're at it.

Happy Migrations and Good Luck.
