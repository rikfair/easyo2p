"""

easyo2p: _tables.py
Extension of the _main.o2p class for creating table statements,
  along with their primary and unique key constraints, and table and column comments.

"""

# -----------------------------------------------

from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List

import easyo2p
from easyo2p import COLUMN, CONSTRAINT, ETL_COMMENTS, ETL_CONSTRAINTS, SEQUENCE, TABLE
if TYPE_CHECKING:
    from easyo2p import O2P

# -----------------------------------------------


def _process_create_comments_cols(o2p: O2P, table_name: str):
    """ Builds the create column comment statements """

    pgs_table_name = o2p.rename_object(TABLE, table_name)

    query = (
        "SELECT column_name, REPLACE(comments, '''', '''''') comments "
        "  FROM user_col_comments "
        f"WHERE table_name = '{table_name}'"
    )

    records, cols = o2p.oracle_query(query, True)

    for record in records:
        column_name = record[cols['column_name']]
        if o2p.is_excluded(COLUMN, f'{table_name}.{column_name}'):
            continue

        comments = record[cols['comments']]
        if comments:
            pgs_column_name = o2p.rename_column(table_name, column_name)
            comments = comments.replace('\n', ' ')
            o2p.postgresql_cmd(
                f"COMMENT ON COLUMN %%schema%%.{pgs_table_name}.{pgs_column_name} IS '{comments}';"
            )


# -----------------------------------------------


def _process_create_comments_tab(o2p: O2P, table_name: str):
    """ Builds the create table comment statement """

    pgs_table_name = o2p.rename_object(TABLE, table_name)

    query = (
        "SELECT REPLACE(comments, '''', '''''') comments"
        "  FROM user_tab_comments "
        f"WHERE table_name = '{table_name}'"
    )

    records = o2p.oracle_query(query)

    for comment in [i[0] for i in records if i[0]]:
        comment = comment.replace('\n', ' ')
        o2p.postgresql_cmd(f"\nCOMMENT ON TABLE %%schema%%.{pgs_table_name} IS '{comment}';\n")


# -----------------------------------------------

def _add_puk_constraint(o2p: O2P, table_name: str, constraint_data: Dict):
    """ Executes the statement to create the primary key """

    if not constraint_data:
        return

    constraint_name = constraint_data['constraint_name']
    if o2p.is_excluded(CONSTRAINT, constraint_name):
        return

    pgs_table_name = o2p.rename_object(TABLE, table_name)
    pgs_constraint_name = o2p.rename_object(CONSTRAINT, constraint_name)
    pgs_columns = ','.join([o2p.rename_column(table_name, i) for i in constraint_data['columns']])
    constraint_type = 'PRIMARY KEY' if constraint_data['constraint_type'] == 'P' else 'UNIQUE'
    tablespace_name = o2p.tablespace_map(
        object_type='INDEX',
        object_name=constraint_name,
        tablespace_name=constraint_data['tablespace_name'],
        preamble=' USING INDEX TABLESPACE '
    )

    o2p.postgresql_cmd((
        f"ALTER TABLE %%schema%%.{pgs_table_name}"
        f" ADD CONSTRAINT {pgs_constraint_name} {constraint_type} "
        f"({pgs_columns}){tablespace_name};"
    ))


# ---


def _process_create_puks(o2p: O2P, table_name: str):
    """ Builds the primary and unique key constraint statements """

    query = (
        "SELECT uc.constraint_name, uc.constraint_type, ucc.column_name, ui.tablespace_name"
        "  FROM user_constraints uc, user_cons_columns ucc, user_indexes ui"
        " WHERE uc.constraint_type IN ('P','U')"
        f"  AND uc.table_name = '{table_name}'"
        "   AND uc.constraint_name = ucc.constraint_name"
        "   AND uc.index_name = ui.index_name"
        " ORDER BY uc.constraint_name, ucc.position"
    )

    constraint_data = {}
    constraint_name = ''

    constraints, cols = o2p.oracle_query(query, True)

    for constraint in constraints:
        if constraint_name != constraint[cols['constraint_name']]:
            _add_puk_constraint(o2p, table_name, constraint_data)
            constraint_name = constraint[cols['constraint_name']]
            constraint_data = {
                'constraint_name': constraint_name,
                'constraint_type': constraint[cols['constraint_type']],
                'columns': [],
                'tablespace_name': constraint[cols['tablespace_name']]
            }
        constraint_data['columns'].append(
            o2p.rename_column(table_name, constraint[cols['column_name']])
        )

    _add_puk_constraint(o2p, table_name, constraint_data)


# -----------------------------------------------


def _get_column_sequence(o2p: O2P, tab_col: str):
    """ Adds the seqeunce to the column, if applicable """

    if tab_col in (tab_seqs := o2p.get_parameter('_table_sequences')):
        pgs_sequence = o2p.rename_object(SEQUENCE, tab_seqs[tab_col])
        return f" DEFAULT NEXTVAL('%%schema%%.{pgs_sequence}')"
    return ''


# -----------------------------------------------


def _get_number_datatype(pgs_column_name: str, record: dict, cols: dict) -> str:
    """ Converts Oracle Number datatype to specific PostgreSQL datatypes """

    data_type = record[cols['data_type']]

    if data_type in ['BINARY_DOUBLE', 'BINARY_FLOAT']:
        return f"FLOAT({'4' if data_type == 'BINARY_FLOAT' else '8'})"
    if data_type == 'FLOAT':
        return "FLOAT(8)"

    # ---

    data_precision = record[cols['data_precision']]
    data_scale = record[cols['data_scale']]

    if data_precision and data_scale:
        datatype = f"NUMERIC({data_precision},{data_scale})"
    elif data_precision:
        if record[cols['column_name']].endswith('_ID'):
            datatype = "INTEGER"
        elif data_precision < 5:
            datatype = "SMALLINT"
        elif data_precision > 9:
            datatype = "BIGINT"
        else:
            datatype = "INTEGER"
        if data_precision < 9:
            datatype += f" CHECK ({pgs_column_name} < {'1' + ('0' * data_precision)})"
    else:
        datatype = "NUMERIC"

    return datatype


# -----------------------------------------------


def _include_column(o2p: O2P, table_name: str, column_name: str):
    """ Returns the column name or False, if the column is excluded """

    if o2p.is_excluded(COLUMN, f'{table_name}.{column_name}'):
        return False
    return o2p.rename_column(table_name, column_name)


# -----------------------------------------------


def _column_order(o2p: O2P, table_name: str):
    """ Creates the user_tab_columns order by clause """

    param = o2p.get_parameter(easyo2p.COLUMN_REORDER)
    if param and (column_reorder := param.get(table_name)):
        return (
            '(CASE column_name '
            + ''.join([f"WHEN '{cn}' THEN {i} " for i, cn in enumerate(column_reorder)])
            + f'ELSE {len(column_reorder)} END), column_id'
        )
    return 'column_id'


# -----------------------------------------------


def _process_create_table(o2p: O2P, table_name: str, columns: List):
    """ Builds the create table statement """

    lines = []

    column_datatypes = {
        j[0]: j[1] for j in [
            i.split(' ') for i in o2p.get_parameter(easyo2p.COLUMN_DATATYPES)
            if i.startswith(f'{table_name}.')
        ]}

    # ---

    query = (
        "SELECT column_name, data_type, data_length, data_precision, data_scale, nullable"
        "  FROM user_tab_columns "
        f"WHERE table_name = '{table_name}'"
        f" ORDER BY {_column_order(o2p, table_name)}"
    )

    records, cols = o2p.oracle_query(query, True)

    # ---

    for record in records:

        ora_column_name = record[cols['column_name']]
        tab_col = f'{table_name}.{ora_column_name}'

        if not (pgs_column_name := _include_column(o2p, table_name, ora_column_name)):
            continue

        data_type = record[cols['data_type']]
        columns.append(ora_column_name)
        line = f", {pgs_column_name}".ljust(35)

        if tab_col in column_datatypes:
            line += column_datatypes[tab_col]
        elif data_type in ['BINARY_DOUBLE', 'BINARY_FLOAT', 'FLOAT', 'NUMBER']:
            line += _get_number_datatype(pgs_column_name, record, cols)
        elif 'CHAR' in data_type:
            line += f"VARCHAR({record[cols['data_length']]})"
        elif data_type == 'DATE':
            line += "TIMESTAMP(0)"
        elif data_type.startswith('TIMESTAMP'):
            line += record[cols['data_type']]
        elif data_type in ['CLOB', 'NCLOB', 'LONG']:
            line += "TEXT"
        elif record[cols['data_type']] in ['BLOB', 'LONG RAW']:
            line += "BYTEA"
        else:
            o2p.log(f"Unknown column: {tab_col}, {data_type}")
            line += "UNKNOWN"

        if record[cols['nullable']] == 'N':
            line += ' NOT NULL'

        line += _get_column_sequence(o2p, tab_col)
        lines.append(line)

    # ---

    o2p.postgresql_cmd((
        f"CREATE TABLE %%schema%%.{o2p.rename_object(TABLE, table_name)} \n("
        + ('\n'.join(lines)).lstrip(',')
        + f"\n) {o2p.get_parameter('_tables')[table_name]}\n;\n"
    ))


# -----------------------------------------------


def main(o2p: O2P, table_name: str, columns: List):
    """ Creates a set of sql files for creating tables in postgresql """

    _process_create_table(o2p, table_name, columns)
    if o2p.get_parameter(ETL_CONSTRAINTS):
        _process_create_puks(o2p, table_name)
    if o2p.get_parameter(ETL_COMMENTS):
        _process_create_comments_tab(o2p, table_name)
        _process_create_comments_cols(o2p, table_name)


# -----------------------------------------------
# End.
