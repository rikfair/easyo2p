"""

Easy, quick and simply Oracle to PostgreSQL schema migration tool.

Migrates a schema's tables, data, constraints, indexes, comments, sequences and (some) triggers.

Connect to both Oracle and PostgreSQL databases simultaneously to migrate in realtime,
create sql script files from the Oracle schema to run repeatedly on PostgreSQL, or both.

"""

# -----------------------------------------------

from easyo2p._constants import *
import easyo2p._main
O2P = easyo2p._main.O2P      # pylint: disable=protected-access      # Protected to limit main usage

# -----------------------------------------------

__version__ = '1.0.0'

# -----------------------------------------------
# End.
