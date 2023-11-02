"""
queries.py
==========

This tutorial expands on the base.py script, creating  how to build parameter lists using queries.
Two new functions have been added to find the relationships between sequences and columns.
Here we assume columns are being populated by sequences using triggers,
  and that the triggers are suffixed _SEQTRG.
This is quite specific but can easily be modified to fit other scenarios.

"""
# -----------------------------------------------

import datetime
import os
import re

import easyo2p

# -----------------------------------------------

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


def _get_sequence_column(o2p: easyo2p.O2P, trigger_name: str):
    """ Finds the column to attach the sequence to by looking for the reference to NEW """

    query = f"SELECT us.text FROM user_source us WHERE us.name = '{trigger_name}'"
    data = o2p.oracle_query(query)

    for d in [i[0] for i in data]:
        columns = re.findall(r'NEW\.(.*):=', d.replace(' ', '').upper())
        if len(columns) == 1:
            return columns[0]

    return None


# ---


def _get_table_sequences(etl: easyo2p.O2P):
    """ Gets sequences based on details """

    query = (
        "SELECT ut.table_name, us.sequence_name, ut.trigger_name"
        "  FROM user_triggers ut,"
        "       user_dependencies ud,"
        "       user_sequences us"
        " WHERE ut.trigger_name LIKE '%SEQTRG'"
        "   AND ut.trigger_name = ud.name"
        "   AND ud.referenced_type = 'SEQUENCE'"
        "   AND ud.referenced_name = us.sequence_name"
    )

    data = etl.oracle_query(query)

    for i, d in enumerate(data):
        data[i] = [*d, _get_sequence_column(etl, d[2])]

    table_sequences = [f'{d[1]} {d[0]}.{d[3]}' for d in data]  # 'sequence table.column'

    return table_sequences


# -----------------------------------------------


def go():
    """ Export just DDL statements """

    # ---
    #  Setup the parameters we're going to use.
    #  Using the date ensures a new directory is used for each run.

    now = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')

    parameters = {
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

    table_sequences = _get_table_sequences(etl)
    etl.set_parameter(easyo2p.SEQUENCES, table_sequences)

    #  ---> Insert code snippets for steps 2, 3, 4, and 5 here.

    #  <---

    etl.do_etl()

    etl.create_run_script()


# -----------------------------------------------

if __name__ == '__main__':
    go()

# -----------------------------------------------
# End.
