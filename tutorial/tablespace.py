"""
tablespace.py
=============

This example outputs the DDL statements to files in the ETL directory
and creates the objects directly on PostgreSQL, using the ``TABLESPACE_MAP`` parameter.
Each run creates a new ETL directory under the specified path, based on the date and time.

"""
# -----------------------------------------------

import datetime
import os

import easyo2p

# -----------------------------------------------
#  Modify values in this section as applicaable to your local settings

ETL_PATH = "C:/Temp/EasyO2P/"                            # <--- Output location
ORACLE_INSTANT_CLIENT = "C:/oracle/instantclient_12_1"   # <--- Adjust to local location

ORAUSER = 'scott'
ORAPASS = 'tiger'
ORAPORT = '1521'                     # <--- Change if your port is not 1521
ORAHOST = '<specific host>'          # <--- Change to your server
ORADBASE = '<specific database>'     # <--- Change to your database

PGSSCHEMA = 'scott'
PGSDBASE = 'easyo2p_db'
PGSUSER = 'easyo2p_user'
PGSPASS = 'easyo2p_pwd'
PGSPORT = '5432'                     # <--- Change if your port is not 5432
PGSHOST = '<specific host>'          # <--- Change to your server

# -----------------------------------------------


def go():
    """ Main function to run the migration """

    # ---
    #  Setup of the parameters that are going to be used.
    #  Using the date ensures a new directory is used for each run.

    now = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')

    parameters = {
        # Tablespace mapping
        easyo2p.TABLESPACE_MAP: [
            'EMP pgtbs_emp',
            'PK_EMP pgtbs_emp',
            'INDEX.EMP_ENAME_IDX pgtbs_emp',
            'DEFAULT pgtbs_tables1',
            'TABLE pg_default',
            'INDEX pgtbs_indexes1',
        ],

        # Rename the limit column created in step 5.
        easyo2p.RENAME: ['COLUMN BONUS.LIMIT BONUS_LIMIT'],

        # Connection info
        easyo2p.ORACLE_INSTANT_CLIENT: ORACLE_INSTANT_CLIENT,
        easyo2p.ORACLE_CONN: f"{ORAUSER}/{ORAPASS}@{ORAHOST}:{ORAPORT}/{ORADBASE}",
        easyo2p.POSTGRES_CONN: (
            f"dbname='{PGSDBASE}' user='{PGSUSER}' host='{PGSHOST}' "
            f"password='{PGSPASS}' port='{PGSPORT}'"
        ),
        easyo2p.POSTGRES_SCHEMA: PGSSCHEMA,
        easyo2p.TARGET_PATH: os.path.join(ETL_PATH, 'exports', now)
    }

    etl = easyo2p.O2P(**parameters)
    etl.do_etl()
    etl.create_run_script()


# -----------------------------------------------

if __name__ == '__main__':
    go()

# -----------------------------------------------
# End.
