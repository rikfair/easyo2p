"""

easyo2p: _indexes.py
Extension of the _main.o2p class for creating index statements

"""

# -----------------------------------------------

from __future__ import annotations
from typing import TYPE_CHECKING, List

from easyo2p import INDEX, TABLE
if TYPE_CHECKING:
    from easyo2p import O2P

# -----------------------------------------------


def _add_index(o2p: O2P, table_name: str, index_name: str, cols: List, tbs: str):
    """ Executes the create index statement """

    if index_name and not o2p.is_excluded(INDEX, index_name):
        tablespace_name = o2p.tablespace_map(INDEX, index_name, tbs)
        pgs_index_name = o2p.rename_object(INDEX, index_name)
        pgs_table_name = o2p.rename_object(TABLE, table_name)

        o2p.postgresql_cmd((
            f"CREATE INDEX {pgs_index_name} ON %%schema%%.{pgs_table_name}"
            f"({','.join(cols)}) {tablespace_name};"
        ))


# -----------------------------------------------


def main(o2p, table_name: str):
    """ Builds the indexes """

    query = (
        "SELECT ui.index_name, uic.column_name, ui.tablespace_name"
        "  FROM user_indexes ui, user_ind_columns uic"
        " WHERE ui.uniqueness = 'NONUNIQUE'"
        "   AND ui.index_type = 'NORMAL'"
        f"  AND ui.table_name = '{table_name}'"
        "   AND ui.index_name = uic.index_name"       
        " ORDER BY ui.index_name, uic.column_position"
    )

    records, cols = o2p.oracle_query(query, True)

    columns = []
    index_name = source_tbs = ''

    for record in records:
        if index_name != record[cols['index_name']]:
            _add_index(o2p, table_name, index_name, columns, source_tbs)
            index_name = record[cols['index_name']]
            source_tbs = record[cols['tablespace_name']]
            columns = []
        columns.append(record[cols['column_name']])

    _add_index(o2p, table_name, index_name, columns, source_tbs)


# -----------------------------------------------
# End.
