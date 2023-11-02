REM -- Replacement function for the Oracle SQL%ROWCOUNT functionality.
REM -- Needs code changes to name and braces appended, which is done by default.


CREATE OR REPLACE FUNCTION %%schema%%.sql_rowcount()
RETURNS DATE
LANGUAGE plpgsql
AS
$$
DECLARE
  num_rows     INTEGER;
BEGIN
  GET DIAGNOSTICS num_rows = ROW_COUNT;
  RETURN num_rows;
END;
$$
;
