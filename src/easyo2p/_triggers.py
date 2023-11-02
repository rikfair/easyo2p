"""

easyo2p: _triggers.py
Extension of the _main.o2p class for creating trigger functions and statements

"""

# -----------------------------------------------

from __future__ import annotations
from typing import TYPE_CHECKING, Dict
import re

from easyo2p import TABLE, TRIGGER
if TYPE_CHECKING:
    from easyo2p import O2P

# -----------------------------------------------


def _get_pgsised_code(o2p: O2P, text: str) -> str:
    """ Replace Oracle code strings """

    for key, val in o2p.get_pls2pgs().items():
        text = text.replace(key, val).replace(key.lower(), val)

    return text


# -----------------------------------------------


def _process_trg_function(o2p: O2P, trigger_name: str):
    """ Builds a trigger function from the Oracle code """

    query = (
        "SELECT us.text"
        "  FROM user_source us "
        f"WHERE us.name = '{trigger_name}'"
        " ORDER BY us.line"
    )

    ora_text = [i[0] for i in o2p.oracle_query(query)]
    pgs_text = ''
    body = False

    # ---

    for line in ora_text:
        if not body and line.strip().upper() in ['DECLARE', 'BEGIN']:
            body = True
        if body:
            if line.strip().upper() == 'END;':
                pgs_text += '  RETURN NEW; \n'
            pgs_text += _get_pgsised_code(o2p, line)
        elif line.strip().upper().endswith(' DECLARE'):
            pgs_text += 'DECLARE \n'
            body = True
        elif line.strip().upper().endswith(' BEGIN'):
            pgs_text += 'BEGIN \n'
            body = True

    # ---

    loop_vars = re.findall(r'\n\s*FOR\s+(\w+)\s+IN', pgs_text)

    if loop_vars:
        declare_loop_vars = '\n'.join(f'  {i} RECORD;' for i in loop_vars) + '\nBEGIN'
        if pgs_text.upper().startswith('BEGIN'):
            declare_loop_vars = '\nDECLARE' + declare_loop_vars
        pgs_text = re.sub('BEGIN', declare_loop_vars, pgs_text, count=1, flags=re.I + re.M)

    # ---

    pgs_trigger_name = o2p.rename_object(TRIGGER, trigger_name)

    cmd = '\n'.join([
        f"CREATE FUNCTION %%schema%%.{pgs_trigger_name}_TF()",
        "RETURNS TRIGGER",
        "LANGUAGE PLPGSQL",
        "AS",
        "$$",
        pgs_text,
        "$$; \n\n"
    ])

    o2p.postgresql_cmd(cmd)


# -----------------------------------------------


def _process_trg_trigger(o2p: O2P, trigger: Dict):
    """ Creates the trigger stub """

    ba_clause = trigger['trigger_type'].split(' ', 1)[0]
    er_clause = 'FOR EACH ROW' if trigger['trigger_type'].endswith('EACH ROW') else ''
    wh_clause = f"WHEN ({trigger['when_clause']})" if trigger['when_clause'] else ''

    pgs_table_name = o2p.rename_object(TABLE, trigger['table_name'])
    pgs_trigger_name = o2p.rename_object(TRIGGER, trigger['trigger_name'])

    cmd = '\n'.join([
        f"CREATE TRIGGER {pgs_trigger_name}",
        f"{ba_clause} {trigger['triggering_event']} ",
        f"ON %%schema%%.{pgs_table_name} {er_clause} {wh_clause}",
        f"EXECUTE PROCEDURE %%schema%%.{pgs_trigger_name}_TF(); \n\n"
    ])

    o2p.postgresql_cmd(cmd)


# -----------------------------------------------


def main(o2p: O2P, table_name: str):
    """ Builds the triggers """

    for trigger in [i for i in o2p.get_parameter('_triggers') if i['table_name'] == table_name]:
        _process_trg_function(o2p, trigger['trigger_name'])
        _process_trg_trigger(o2p, trigger)


# -----------------------------------------------
# End.
