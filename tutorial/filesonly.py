"""
filesonly.py
============

This example outputs the DDL statements to files in the ETL directory.
Each run creates a new ETL directory under the specified path, based on the date and time.

"""
# -----------------------------------------------

import datetime
import os

import easyo2p

# -----------------------------------------------

ETL_PATH = "C:/Temp/EasyO2P/"                            # <--- Output location
ORACLE_INSTANT_CLIENT = "C:/oracle/instantclient_12_1"   # <--- Adjust to local location

ORAUSER = 'scott'
ORAPASS = 'tiger'
ORAPORT = '1521'                     # <--- Change if your port is not 1521
ORAHOST = '<specific host>'          # <--- Change to your server
ORADBASE = '<specific database>'     # <--- Change to your database

# -----------------------------------------------


def go():
    """ Main function to run the migration """

    # ---
    #  Setup of the parameters that are going to be used.
    #  Using the date ensures a new directory is used for each run.

    now = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')

    parameters = {
        # Runtime options
        easyo2p.ETL_DATA: False,   # <--- Change to True to create data scripts too
        easyo2p.ETL_FILES: True,
        easyo2p.ETL_MIGRATE: False,

        # Connection info
        easyo2p.ORACLE_INSTANT_CLIENT: ORACLE_INSTANT_CLIENT,
        easyo2p.ORACLE_CONN: f"{ORAUSER}/{ORAPASS}@{ORAHOST}:{ORAPORT}/{ORADBASE}",
        easyo2p.POSTGRES_SCHEMA: 'scott',
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
