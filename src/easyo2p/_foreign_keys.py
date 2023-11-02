"""

easyo2p: _foreign_keys.py
Extension of the _main.o2p class for adding foreign key constraints

"""

# -----------------------------------------------

from __future__ import annotations
from typing import TYPE_CHECKING, Dict

from easyo2p import CONSTRAINT, TABLE, TABLES
if TYPE_CHECKING:
    from easyo2p import O2P

# -----------------------------------------------


def _add_fk_constraint(o2p: O2P, table_name: str, constraint_data: Dict):
    """ Adds a foreign key constraint """

    if not constraint_data:
        return

    foreign_key_name = o2p.rename_object(CONSTRAINT, constraint_data['constraint_name'])
    if o2p.is_excluded(CONSTRAINT, foreign_key_name):
        return

    pgs_table_name = o2p.rename_object(TABLE, table_name)
    pgs_r_table_name = o2p.rename_object(TABLE, constraint_data['r_table_name'])

    columns = ','.join(constraint_data['columns'])
    r_columns = ','.join(constraint_data['r_columns'])

    o2p.postgresql_cmd((
        f"ALTER TABLE %%schema%%.{pgs_table_name} ADD CONSTRAINT {foreign_key_name} FOREIGN KEY "
        f"({columns}) REFERENCES %%schema%%.{pgs_r_table_name} "
        f"({r_columns}) "
        f"ON DELETE {constraint_data['delete_rule']};"
    ))


# -----------------------------------------------


def main(o2p: O2P, table_name: str):
    """ Builds the primary and unique key constraint statements """

    tables = o2p.get_parameter(TABLES)
    constraint_name = ''
    constraint_data = {}

    query = (
        'SELECT uc.constraint_name, ruc.table_name r_table_name,'
        '       ucc.column_name, rucc.column_name r_column_name, uc.delete_rule'
        '  FROM user_constraints uc,'
        '       user_cons_columns ucc,'
        '       user_constraints ruc,'
        '       user_cons_columns rucc'
        ' WHERE uc.constraint_name = ucc.constraint_name'
        '   AND uc.r_constraint_name = ruc.constraint_name'
        '   AND ruc.constraint_name = rucc.constraint_name'
        '   AND ucc.position = rucc.position'
        f"  AND uc.table_name = '{table_name}'"
        ' ORDER BY uc.constraint_name, ucc.position'
    )

    records, cols = o2p.oracle_query(query, True)

    for record in records:
        if record[cols['r_table_name']] in tables:
            if constraint_name != record[cols['constraint_name']]:
                _add_fk_constraint(o2p, table_name, constraint_data)
                constraint_name = record[cols['constraint_name']]
                constraint_data = {
                    'constraint_name': constraint_name,
                    'columns': [],
                    'r_table_name': o2p.rename_object('TABLE', record[cols['r_table_name']]),
                    'r_columns': [],
                    'delete_rule': record[cols['delete_rule']]
                }

            constraint_data['columns'].append(o2p.rename_column(
                table_name, record[cols['column_name']]
            ))

            constraint_data['r_columns'].append(o2p.rename_column(
                constraint_data['r_table_name'], record[cols['r_column_name']]
            ))

    _add_fk_constraint(o2p, table_name, constraint_data)


# -----------------------------------------------
# End.
