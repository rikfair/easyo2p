REM -- Replacement function for the Oracle RAISE_APPLICATION_ERROR function.
REM -- Needs to be prefixed with the CALL command, which is done by default.


CREATE OR REPLACE PROCEDURE %%schema%%.raise_application_error(en NUMERIC, et VARCHAR)
LANGUAGE plpgsql
AS
$$
DECLARE
  msg  VARCHAR := CAST(en AS VARCHAR) || ': ' || et;
BEGIN
  RAISE EXCEPTION '%', msg;
END;
$$
;
