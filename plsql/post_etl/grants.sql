REM -- Grants set to easyo2p_user, for use with the tutorial. Change this user as required.

DO $$
BEGIN
	GRANT USAGE ON SCHEMA %%schema%% TO easyo2p_user;
	GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA %%schema%% TO easyo2p_user;
	ALTER DEFAULT PRIVILEGES IN SCHEMA %%schema%% GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO easyo2p_user;
	GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA %%schema%% TO easyo2p_user;
	ALTER DEFAULT PRIVILEGES IN SCHEMA %%schema%% GRANT USAGE, SELECT ON SEQUENCES TO easyo2p_user;
END $$;
