REM -- Wrapper functions to replicate Oracle functionality to add/subtract days to/from dates.

REM -- Add days function and operator

CREATE OR REPLACE FUNCTION %%schema%%.timestamp_add_days(
	TIMESTAMP WITH TIME ZONE,
	NUMERIC
) RETURNS TIMESTAMP WITH TIME ZONE
  LANGUAGE 'sql'
  COST 100
  IMMUTABLE PARALLEL UNSAFE
AS
$$
SELECT $1 + interval '1 day' * $2;
$$
;


CREATE OPERATOR %%schema%%.+(
  FUNCTION = %%schema%%.timestamp_add_days,
  LEFTARG = TIMESTAMP WITH TIME ZONE,
  RIGHTARG = NUMERIC
)
;


REM -- Minus days function and operator

CREATE OR REPLACE FUNCTION %%schema%%.timestamp_minus_days(
	TIMESTAMP WITH TIME ZONE,
	NUMERIC
) RETURNS TIMESTAMP WITH TIME ZONE
  LANGUAGE 'sql'
  COST 100
  IMMUTABLE PARALLEL UNSAFE
AS
$$
SELECT $1 - interval '1 day' * $2;
$$
;

CREATE OPERATOR %%schema%%.-(
  FUNCTION = %%schema%%.timestamp_minus_days,
  LEFTARG = TIMESTAMP WITH TIME ZONE,
  RIGHTARG = NUMERIC
)
;
