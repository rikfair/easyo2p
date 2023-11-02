REM -- Wrapper function to mimic the Oracle LAST_DAY function.

CREATE OR REPLACE FUNCTION %%schema%%.last_day(the_date DATE)
RETURNS date
LANGUAGE 'sql'
AS
$$
SELECT (DATE_TRUNC('MONTH', the_date) + INTERVAL '1 MONTH - 1 day')::DATE;
$$
