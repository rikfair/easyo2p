REM -- Wrapper functions for Oracle functionality to truncate dates

CREATE OR REPLACE FUNCTION %%schema%%.trunc(d ANYELEMENT)
RETURNS DATE
LANGUAGE plpgsql
AS
$$
BEGIN
  RETURN DATE_TRUNC('DAY', d);
END;
$$
;


CREATE OR REPLACE FUNCTION %%schema%%.trunc(i INTERVAL)
RETURNS INTEGER
LANGUAGE plpgsql
AS
$$
BEGIN
  RETURN EXTRACT(DAY FROM i);
END;
$$
;
