
CREATE OR REPLACE FUNCTION %%schema%%.to_char(s ANYELEMENT)
RETURNS VARCHAR
LANGUAGE plpgsql
AS
$$
BEGIN
  RETURN CAST(s AS VARCHAR);
END;
$$
