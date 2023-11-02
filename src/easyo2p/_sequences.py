"""

easyo2p: _sequences.py
Extension of the _main.o2p class for creating sequence statements

"""

# -----------------------------------------------

from __future__ import annotations
from typing import TYPE_CHECKING

from easyo2p import SEQUENCE
if TYPE_CHECKING:
    from easyo2p import O2P

# -----------------------------------------------


def main(o2p: O2P):
    """ Creates a set of sql files for creating sequences in postgresql """

    sequences = o2p.get_parameter('_sequences')

    query = (
        "SELECT us.sequence_name, us.increment_by, us.last_number"
        "  FROM user_sequences us"
        " WHERE " + (' OR '.join([f"us.sequence_name = '{i}'" for i in sequences]))
    )

    data = {i[0]: [i[1], i[2]] for i in o2p.oracle_query(query)}

    for i in sorted(list(data)):
        sequence_name = o2p.rename_object(SEQUENCE, i)
        o2p.postgresql_cmd((
            f"CREATE SEQUENCE %%schema%%.{sequence_name} "
            f"INCREMENT {data[i][0]} START {data[i][1] + 1};"
        ))


# -----------------------------------------------
# End.
