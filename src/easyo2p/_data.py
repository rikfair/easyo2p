"""

easyo2p: _data.py
Extension of the _main.o2p class for creating insert statements

"""

# -----------------------------------------------
# Ignoring c-extension-no-member due to issues raised with references to cx_Oracle
# pylint: disable=c-extension-no-member
# -----------------------------------------------

from __future__ import annotations
from typing import TYPE_CHECKING, List
import datetime

import cx_Oracle

from easyo2p import TABLE
if TYPE_CHECKING:
    from easyo2p import O2P

# -----------------------------------------------


def main(o2p: O2P, table_name: str, columns: List, insert_rows: int):
    """ Processes export for a specified table """

    query = f"SELECT {','.join(columns)} FROM {table_name}"
    cursor = o2p.get_oracle_connection().cursor()
    cursor.execute(query)

    while True:
        rows = cursor.fetchmany(insert_rows)
        if not rows:
            break
        rows_to_insert = []

        for row in rows:
            cols = []
            for col in row:
                if col is None:
                    cols.append('NULL')
                elif isinstance(col, bytes):
                    cols.append(f"DECODE('{col.hex()}', 'hex')")
                elif isinstance(col, (str, cx_Oracle.LOB)):
                    cols.append("'" + str(col).replace("'", "''") + "'")
                elif isinstance(col, datetime.datetime):
                    cols.append(
                        f"TO_TIMESTAMP('{col.strftime('%Y%m%d%H%M%S')}','YYYYMMDDHH24MISS')"
                    )
                else:
                    cols.append(str(col))
            rows_to_insert.append(f"({','.join(cols)})")

        # ---

        pgs_table_name = o2p.rename_object(TABLE, table_name)
        pgs_columns = ','.join([o2p.rename_column(table_name, i) for i in columns])

        values = ',\n'.join(rows_to_insert)
        cmd = (
            f"INSERT INTO %%schema%%.{pgs_table_name}"
            f"({pgs_columns}) VALUES \n{values}; \n"
        )
        cmd = cmd.replace('\x00', '')
        o2p.postgresql_cmd(cmd)


# -----------------------------------------------
# End.
