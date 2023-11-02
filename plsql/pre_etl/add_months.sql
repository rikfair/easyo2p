REM -- Replacement function for Oracle ADD_MONTHS


REM -- Add months to dates

CREATE OR REPLACE FUNCTION %%schema%%.add_months(the_date DATE, duration NUMERIC)
RETURNS DATE
LANGUAGE plpgsql
AS
$$
BEGIN
  RETURN the_date + (duration||' MONTH')::INTERVAL;
END;
$$
;


REM -- Add months to timestamps

CREATE OR REPLACE FUNCTION %%schema%%.add_months(the_date TIMESTAMP WITHOUT TIME ZONE, duration NUMERIC)
RETURNS DATE
LANGUAGE plpgsql
AS
$$
BEGIN
  RETURN the_date + (duration||' MONTH')::INTERVAL;
END;
$$
;
