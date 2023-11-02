REM -- Wrapper to convert uses of NVL to use COALESCE

REM -- NVL dates

CREATE FUNCTION %%schema%%.nvl(a DATE, b DATE)
RETURNS DATE
LANGUAGE plpgsql
AS
$$
BEGIN
  RETURN COALESCE(a, b);
END;
$$
;


REM -- NVL numeric

CREATE FUNCTION %%schema%%.nvl(a NUMERIC, b NUMERIC)
RETURNS NUMERIC
LANGUAGE plpgsql
AS
$$
BEGIN
  RETURN COALESCE(a, b);
END;
$$
;


REM -- NVL character

CREATE FUNCTION %%schema%%.nvl(a VARCHAR, b VARCHAR)
RETURNS VARCHAR
LANGUAGE plpgsql
AS
$$
BEGIN
  RETURN COALESCE(a, b);
END; $$
;

