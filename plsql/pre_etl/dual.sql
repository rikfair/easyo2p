REM -- View to replace the Oracle DUAL table.
REM -- Owned by the schema, but references to SYS.DUAL will be replaced by DUAL during the migration by default.


CREATE VIEW %%schema%%.dual AS SELECT 'X' AS DUMMY;
