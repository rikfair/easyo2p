REM -- Wrapper function for the Oracle TO_NUMBER function

REM -- TO_NUMBER any datatype

CREATE OR REPLACE FUNCTION %%schema%%.to_number(a ANYELEMENT)
RETURNS NUMERIC
LANGUAGE plpgsql
AS
$$
BEGIN
  -- Be careful! This will return a decimal place for an integer. '123' returns 123.0
  -- Consider changing the SQL to CAST(s AS INT) instead, which works with both Oracle and Postgresql
  RETURN CAST(a AS NUMERIC);
END;
$$
;


REM -- TO_NUMBER integer

CREATE OR REPLACE FUNCTION %%schema%%.to_number(a INTEGER)
RETURNS INTEGER
LANGUAGE plpgsql
AS
$$
BEGIN
  RETURN a;
END;
$$
;


REM -- TO_NUMBER text

CREATE OR REPLACE FUNCTION %%schema%%.to_number(a TEXT)
RETURNS NUMERIC
LANGUAGE plpgsql
AS
$$
BEGIN
  RETURN CAST(a AS NUMERIC);
END;
$$
;

