"""

easyo2p: _main.py
The O2P class that manages the Oracle to PostgreSQL migration.

"""

# -----------------------------------------------
# Ignoring pylint c-extension-no-member, due to issues raised with references to cx_Oracle
# pylint: disable=c-extension-no-member
# -----------------------------------------------

from typing import Any, Dict, List, Tuple, Union

import datetime
import logging
import os

import cx_Oracle
import psycopg2

from easyo2p._constants import *    # pylint: disable=unused-wildcard-import,wildcard-import
import easyo2p._data as o2p_data
import easyo2p._foreign_keys as o2p_foreign_keys
import easyo2p._indexes as o2p_indexes
import easyo2p._sequences as o2p_sequences
import easyo2p._tables as o2p_tables
import easyo2p._triggers as o2p_triggers

# -----------------------------------------------


class O2P:
    """ Oracle to PostgreSQL migration tools class"""

    # -------------------------------------------

    def __init__(self, **kwargs):
        """
        Initialise the o2p class
        """

        self._conn_ora = None
        self._conn_pgs = []
        self._etl_file = None
        self._stage = PRE
        self._file_number = 0
        self._parameters = _get_parameters(**kwargs)
        self._validate_target_path()

        if self._parameters['_target_path_validated']:
            log_file = os.path.join(self._parameters[TARGET_PATH], '_easyo2p_.log')
            handler = logging.FileHandler(log_file)
            self._logger = logging.getLogger('easyo2p')
            self._logger.setLevel(logging.INFO)
            self._logger.addHandler(handler)
        else:
            self._logger = None

    # -------------------------------------------

    def create_run_script(self):
        """ Creates a sql script ``_run_.sql`` to run all of the scripts created on PostgreSQL. """

        if self._stage != POST:
            raise RuntimeError('Unable to create run script until ETL has been performed')

        if self._parameters[ETL_FILES]:

            schema = self._parameters[POSTGRES_SCHEMA]
            file_name = os.path.join(self._parameters[TARGET_PATH], '_run_.sql')
            run_file_name = file_name.replace('\\', '/')

            script = [f"-- \\i '{run_file_name}' \n"]
            if self._parameters[DROP_SCHEMA]:
                script.append(f"DROP SCHEMA IF EXISTS {schema} CASCADE; \n")

            client_encoding = (
                'UTF8' if self._parameters[ENCODING].upper().replace('-', '').startswith('UTF8')
                else self._parameters[ENCODING]
            )

            script.extend([
                f"CREATE SCHEMA IF NOT EXISTS {schema}; \n"
                f"SET search_path TO {schema}; \n",
                f"SET client_encoding = '{client_encoding}'; \n",
                '\\set AUTOCOMMIT on \n',
            ])

            files = sorted(os.listdir(self._parameters[TARGET_PATH]))

            for file_type in ['.1.sql', '.2.sql', '.3.sql', '.4.sql', '.5.sql', '.6.sql']:
                script.append(f'\n\\echo Processing "{file_type}" files...\n')
                for file in files:
                    if file.endswith(file_type):
                        script.append(f'\\ir {file}')

            script.append('\n')

            self.file_write_from_string(file_name, '\n'.join(script))
            self.log(f"Run: \\i '{run_file_name}'")

    # -------------------------------------------

    def do_etl(self):
        """ Run the etl process, ensure parameters are all set. """

        self._stage = ETL
        self._initialise_parameters()

        # ---
        #  Connections

        self.get_oracle_connection()

        if self._parameters[ETL_MIGRATE]:
            self.get_postgres_connection()

        # ---
        #   ETL 1/3: Sequences

        if self._parameters['_sequences']:
            self._etl_set_file('sequences.2.sql', 'Creating Sequences')
            o2p_sequences.main(self)
            self._etl_close_file()

        # ---
        #   ETL 2/3: Tables and Data

        table_columns = {}

        for table_name in self._parameters[TABLES]:
            pgs_table_name = self.rename_object(TABLE, table_name)
            columns = table_columns[table_name] = []
            self._etl_set_file(f'{pgs_table_name}.3.sql', f'{pgs_table_name} Table')
            o2p_tables.main(self, table_name, columns)
            if self._parameters[ETL_DATA]:
                self._etl_set_file(f'{pgs_table_name}.4.sql', f'{pgs_table_name} Data')
                o2p_data.main(self, table_name, columns, self._parameters[INSERT_ROWS])

        # ---
        #   ETL 3/3: Foreign Keys, Indexes, and Triggers

        for table_name in self._parameters[TABLES]:
            pgs_table_name = self.rename_object(TABLE, table_name)
            etl_file = f'{pgs_table_name}.5.sql'
            if self._parameters[ETL_CONSTRAINTS]:
                self._etl_set_file(etl_file, f'{pgs_table_name} Foreign Keys')
                o2p_foreign_keys.main(self, table_name)
                self._etl_set_file(etl_file, f'{pgs_table_name} Indexes')
                o2p_indexes.main(self, table_name)
            if self._parameters[ETL_TRIGGERS]:
                self._etl_set_file(etl_file, f'{pgs_table_name} Triggers')
                o2p_triggers.main(self, table_name)

        # ---

        self._etl_close_file()
        self._stage = POST

    # -------------------------------------------

    def file_read_to_string(self, filename: str, parameter_map=None) -> str:
        """
        Reads a text file and returns the file content as a string.

        Lines beginning "REM " are ignored

        :param filename: the filename including path.
        :param parameter_map: list of strings to replace in the file.
            Encase strings within the file with %%.
        :return: the file content as a string.
        """

        with open(filename, 'r', encoding=self._parameters[ENCODING], newline='') as file:
            lines = [i.rstrip() for i in file.readlines() if not i.upper().startswith('REM ')]
        text = '\n'.join(lines)

        if parameter_map:
            for i in parameter_map:
                text = text.replace(f'%%{i}%%', self._parameters[i])

        return text

    # -------------------------------------------

    def file_write_from_string(self, filename: str, content: str, mode: str = 'a'):
        """
        Wrapper method for writing a file using the encoding parameter.

        :param filename: the filename including path
        :param content: the string to writeString to write
        :param mode: 'a'ppend, or 'w'rite
        """

        encoding = self._parameters[ENCODING]
        if encoding.lower() == 'utf-8':
            encoding = 'utf-8-sig'  # Loose BOM, as this causes issues for psql.
        with open(filename, mode, encoding=encoding, newline='\n') as text_file:
            text_file.write(content)  # Use write instead of print to avoid trailing new line

    # -------------------------------------------

    def get_parameter(self, name: str) -> Any:
        """
        Get a named parameter value

        :param name: the name of the parameter
        :return: the parameter value if it exists or None
        """

        return self._parameters.get(name)

    # ---

    def set_parameter(self, name: str, value: Union[Any]):
        """
        Sets a single parameter with the specified value
        Settable parameters: EXCLUDE, RENAME, SEQUENCES, TABLES, TABLESPACE_MAP, TRIGGERS

        :param name: the name of the parameter
        :param value: the value of the parameter
        """

        if self._stage != PRE:
            raise RuntimeError('Unable to update parameters after "do_etl"')
        if name not in [
            COLUMN_DATATYPES, COLUMN_REORDER, EXCLUDE, RENAME,
            SEQUENCES, TABLES, TABLESPACE_MAP, TRIGGERS
        ]:
            raise ValueError(f'Parameter "{name}" must be set during initialisation')
        if name.startswith('_'):
            raise ValueError(f'Unable to update parameter "{name}"')
        self._parameters[name] = value

    # -------------------------------------------

    def get_pls2pgs(self) -> Dict:
        """ Gets the current pls2pgs mappings """

        return self._parameters['_pls2pgs']

    # ---

    def set_pls2pgs(self, pls2pgs: Dict, update: bool = True):
        """
        Sets multiple pls2pgs mappings with the specified values

        :param pls2pgs: the names and values of the pls2pgs mappings
        :param update: should the mappings be updated or not, replaced.
        """

        if update:
            self._parameters['_pls2pgs'].update(pls2pgs)
        elif isinstance(pls2pgs, dict):
            self._parameters['_pls2pgs'] = pls2pgs
        else:
            raise ValueError('Dict expected')

        for i in [i for i in self._parameters['_pls2pgs'].values() if i is None]:
            del self._parameters['_pls2pgs'][i]

    # -------------------------------------------

    def get_oracle_connection(self) -> cx_Oracle.connect:
        """
        Gets the cx_oracle connection object

        :return: oracle connection object
        """

        if not self._conn_ora:
            if ORACLE_INSTANT_CLIENT not in self._parameters:
                raise ValueError(f'"{ORACLE_INSTANT_CLIENT}" not set')
            if ORACLE_CONN not in self._parameters:
                raise ValueError(f'"{ORACLE_CONN}" not set')

            encoding = (
                'UTF8' if self._parameters[ENCODING].upper().replace('-', '').startswith('UTF8')
                else self._parameters[ENCODING]
            )

            cx_Oracle.init_oracle_client(lib_dir=self._parameters[ORACLE_INSTANT_CLIENT])
            self._conn_ora = cx_Oracle.connect(self._parameters[ORACLE_CONN], encoding=encoding)
            self._conn_ora.outputtypehandler = _output_type_handler

        return self._conn_ora

    # -------------------------------------------

    def get_postgres_connection(self, conn_number: int = 0) -> psycopg2.connect:
        """
        Creates the psycopg2 connection to PostgreSQL

        :return: psycopg2 connection object
        """

        if not self._conn_pgs:
            self.postgresql_init_schema()

        return self._conn_pgs[conn_number]

    # -------------------------------------------

    def is_excluded(self, object_type: str, object_name: str) -> bool:
        """ Checks to see if object is in the exclude list """

        return f'{object_type} {object_name}' in self._parameters[EXCLUDE]

    # -------------------------------------------

    def oracle_query(self, query: str, inc_cols: bool = False) -> Union[Tuple[List, List], List]:
        """
        Executes a query on the Oracle database

        :param query: the query string
        :param inc_cols: should a tuple be returned which also includes the columns and positions
        :return: data or tuple of data and column names
        """

        conn = self.get_oracle_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        columns = {c[0].lower(): i for i, c in enumerate(cursor.description)} if inc_cols else None
        data = list(cursor.fetchall())
        cursor.close()

        return (data, columns) if inc_cols else data

    # -------------------------------------------

    def postgresql_cmd(self, cmd: str, filename: str = ''):
        """
        Executes a PostgreSQL DDL or DML command. Either to a file, postgresql database, or both.

        :param cmd: the command string.
        :param filename: the ETL filename to write the command to.
        """

        cmd = cmd.replace('%%schema%%', self._parameters[POSTGRES_SCHEMA])

        if self._stage != ETL and self._parameters[ETL_FILES]:
            filename = filename or 'postgresql_cmd'
            self._etl_set_file(filename, f'PostgreSQL Cmd: {os.path.basename(filename)}')

        self._etl_write(cmd + '\n')

        if self._parameters[ETL_MIGRATE]:
            if not self._conn_pgs:
                self.postgresql_init_schema()
            for conn in self._conn_pgs:
                conn.cursor().execute(cmd)

    # -----------------------------------------------

    def postgresql_file(self, file_path):
        """
        Executes the command file on PostgreSQL and/or outputs command to ETL file.

        :param file_path: the path and name of the file to execute
        """

        cmd = self.file_read_to_string(file_path)
        self.postgresql_cmd(cmd, file_path)

    # -----------------------------------------------

    def postgresql_init_schema(self):
        """
        Creates PostgreSQL schema, dropping it first if it already exists
        """

        if not self._conn_pgs:

            schema = self._parameters[POSTGRES_SCHEMA]
            if not schema:
                raise ValueError('Invalid PostgreSQL schema')

            if isinstance(self._parameters[POSTGRES_CONN], str):
                self._parameters[POSTGRES_CONN] = [self._parameters[POSTGRES_CONN]]

            self._conn_pgs = []
            for conn_string in self._parameters[POSTGRES_CONN]:
                conn = psycopg2.connect(conn_string)
                conn.set_session(autocommit=True)
                if self._parameters[DROP_SCHEMA]:
                    conn.cursor().execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
                conn.cursor().execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
                self._conn_pgs.append(conn)

    # -------------------------------------------

    def rename_column(self, table_name: str, column_name: str):
        """ rename_object wrapper for columns """

        renamed = self.rename_object(COLUMN, f'{table_name}.{column_name}')
        return renamed.split('.', 1)[1] if '.' in renamed else renamed

    # -------------------------------------------

    def rename_object(self, object_type: str, object_name: str):
        """ Overrides the object name with the rename value, if one exists """

        return self._parameters['_rename'].get(f'{object_type} {object_name}', object_name)

    # -------------------------------------------

    def tablespace_map(self, object_type: str, object_name: str,
                       tablespace_name: str, preamble: str = 'TABLESPACE ') -> str:
        """
        Maps existing tablespaces to target tablespace

        :param object_type: either TABLE or INDEX
        :param object_name: the name of the object
        :param tablespace_name: the tablespace name to map
        :param preamble: text to place before the tablespace name if being used.
        :return: the target tablespace name
        """

        if not self._parameters['_tablespace_map']:
            return ''

        search = [object_type, object_name, f'{object_type}.{object_name}', tablespace_name]
        for i in self._parameters['_tablespace_map']:
            if i[0] in search:
                return i[1]

        return preamble + tablespace_name

    # -------------------------------------------

    def log(self, comment: str):
        """ Log a comment to the log file and console if ``console`` parameter True """

        if self._logger is not None:
            self._logger.info(comment)
        if self._parameters.get(CONSOLE):
            print(f'{datetime.datetime.now()}: {comment}')

    # -------------------------------------------

    def _etl_set_file(self, filename: str, msg: str):
        """ Sets the file to spool output to. """

        self.log(msg)

        if self._parameters[ETL_FILES]:
            if not self._etl_file or (self._etl_file and self._etl_file[0] != filename):
                if self._etl_file:
                    self._etl_close_file()
                if self._stage != ETL:
                    self._file_number += 1
                    filename = (
                        f"{str(self._file_number).zfill(6)}."
                        f"{os.path.basename(filename).rsplit('.', 1)[0]}"
                        f".{self._stage}.sql"
                    )
                filepath = os.path.join(self._parameters[TARGET_PATH], filename)

                # pylint: disable=consider-using-with        # Need to keep file open after method
                self._etl_file = (
                    filename,
                    open(filepath, 'a', encoding=self._parameters[ENCODING])
                )

            if msg:
                self._etl_write(f'\n\\echo {msg}\n\n')

    # ---

    def _etl_write(self, string: str):
        """ Writes ETL data to the appropriate file """

        if self._etl_file:
            self._etl_file[1].write(string)

    # ---

    def _etl_close_file(self):
        """ Closes the current ETL file """

        if self._etl_file:
            self._etl_file[1].close()
            self._etl_file = None

    # -------------------------------------------

    def _initialise_parameters(self):
        """ Sets defaults and removes exclusions """

        # ---
        #  Column Datatypes

        if COLUMN_DATATYPES not in self._parameters:
            self._parameters[COLUMN_DATATYPES] = []

        # ---
        #  Exclude

        if EXCLUDE not in self._parameters:
            self._parameters[EXCLUDE] = []

        # ---
        #  Rename

        self._parameters['_rename'] = {}
        if RENAME in self._parameters:
            for i in self._parameters[RENAME]:
                key, val = i.rsplit(' ', 1)
                self._parameters['_rename'][key] = val

        # ---
        #  Sequences

        if SEQUENCES in self._parameters and isinstance(self._parameters[SEQUENCES], bool):
            if self._parameters[SEQUENCES]:
                del self._parameters[SEQUENCES]    # True not required, included by default.
            else:
                self._parameters[SEQUENCES] = []   # No sequences is same as do not include.

        if SEQUENCES in self._parameters:
            self._parameters['_table_sequences'] = {
                i2[1]: i2[0]
                for i2 in [(i1.split(' ', 1)) for i1 in self._parameters[SEQUENCES] if ' ' in i1]
                if '.' in i2[1]
            }
            self._parameters['_sequences'] = [
                (i.split(' ', 1))[0] for i in self._parameters[SEQUENCES]
            ]

        else:
            self._populate_sequences()
            self._parameters['_table_sequences'] = {}
            self._parameters[SEQUENCES] = []

        self._remove_excluded_from_list(SEQUENCE, '_sequences')

        # ---
        #  Tablespaces

        self._parameters['_tablespace_map'] = [
            i.split(' ') for i in self._parameters[TABLESPACE_MAP]
        ] if self._parameters[TABLESPACE_MAP] else None

        # ---
        #  Tables

        self._populate_tables()
        self._remove_excluded_from_list(TABLE, TABLES)

        # ---
        #  Identity Sequences

        self._populate_identity_sequences()

        # ---
        #  Triggers

        self._parameters[ETL_TRIGGERS] = (
                self._parameters[ETL_TRIGGERS] or bool(self._parameters.get(TRIGGERS))
        )

        if not self._parameters[ETL_TRIGGERS]:
            self._parameters[TRIGGERS] = []
        else:
            self._populate_triggers()

    # -------------------------------------------

    def _populate_identity_sequences(self):
        """ Populates the sequences parameter for identity columns """

        tables = self._parameters[TABLES]
        exclude = self._parameters[EXCLUDE]

        query = (
            "SELECT table_name, column_name, sequence_name "
            "  FROM user_tab_identity_cols"
        )

        try:
            for i in self.oracle_query(query):
                if (tab_col := f'{i[0]}.{i[1]}') not in exclude and i[0] in tables:
                    if i[2] not in self._parameters['_sequences']:
                        self._parameters['_sequences'].append(i[2])
                    self._parameters['_table_sequences'][tab_col] = i[2]
        except cx_Oracle.DatabaseError:
            pass  # Assume pre Oracle 12 database

    # -------------------------------------------

    def _populate_sequences(self):
        """ Gets all the sequence names from the user_sequences view """

        query = "SELECT sequence_name FROM user_sequences"
        self._parameters['_sequences'] = [i[0] for i in self.oracle_query(query)]

    # -------------------------------------------

    def _populate_tables(self):
        """ Gets all the table names from the user_tables view """

        query = (
            "SELECT ut.table_name, ut.tablespace_name"
            "  FROM user_tables ut"
            " WHERE ut.status = 'VALID'"
            "   AND tablespace_name IS NOT NULL"
            "   AND SUBSTR(table_name,1,4) != 'SYS_'"
            " ORDER BY 1"
        )
        data = {i[0]: self.tablespace_map(TABLE, i[0], i[1]) for i in self.oracle_query(query)}
        if self._parameters.get(TABLES):
            self._parameters['_tables'] = {
                i: self.tablespace_map(TABLE, i, data.get(i)) for i in self._parameters[TABLES]
            }
        else:
            self._parameters[TABLES] = list(data)
            self._parameters['_tables'] = data

    # -------------------------------------------

    def _populate_triggers(self):
        """ Gets all the trigger names from the user_triggers view """

        triggers = (
            ' OR '.join([f"trigger_name = '{i}'" for i in self._parameters[TRIGGERS]])
            or ' 1=1 '
        )

        query = (
            "SELECT ut.table_name,"
            "       ut.trigger_name,"
            "       ut.trigger_type,"
            "       ut.triggering_event,"
            "       ut.when_clause"
            "  FROM user_triggers ut"
            " WHERE ut.status = 'ENABLED'"
            "   AND ut.base_object_type = 'TABLE'"
            f"  AND ({triggers})"
        )

        self._parameters['_triggers'] = [{
            'table_name': i[0],
            'trigger_name': i[1],
            'trigger_type': i[2],
            'triggering_event': i[3],
            'when_clause': i[4]
        } for i in self.oracle_query(query) if f'TRIGGER {i[1]}' not in self._parameters[EXCLUDE]]

    # -------------------------------------------

    def _remove_excluded_from_list(self, object_type: str, parameter_name: str):
        """ Remove excluded objects from the list """

        if self._parameters[parameter_name]:
            exclusions = {
                i.split(' ', 1)[1] for i in self._parameters[EXCLUDE]
                if i.startswith(f'{object_type} ')
            }
            if exclusions:
                # Using a list comprehension rather than sets to preserve order
                inclusions = [i for i in self._parameters[parameter_name] if i not in exclusions]
                self._parameters[parameter_name] = inclusions

    # -------------------------------------------

    def _validate_target_path(self):
        """ Validates the target path and creates required directoeies """

        if self._parameters[ETL_FILES]:
            if not self._parameters[TARGET_PATH]:
                raise ValueError('Target path not set')
        if TARGET_PATH in self._parameters and not self._parameters['_target_path_validated']:
            self._parameters[TARGET_PATH] = os.path.normpath(self._parameters[TARGET_PATH])
            if os.path.exists(self._parameters[TARGET_PATH]):
                raise ValueError(f'Target path exists: "{self._parameters[TARGET_PATH]}"')
            os.makedirs(self._parameters[TARGET_PATH])
            self._parameters['_target_path_validated'] = True


# -----------------------------------------------


def _get_parameters(**kwargs) -> Dict:
    """ Parameters dictionary with default and specified values """

    parameters = {
        CONSOLE: True,
        DROP_SCHEMA: True,
        ENCODING: 'utf-8-sig',
        ETL_CONSTRAINTS: True,
        ETL_COMMENTS: True,
        ETL_DATA: True,
        ETL_FILES: True,
        ETL_MIGRATE: True,
        ETL_TRIGGERS: False,
        INSERT_ROWS: 10_000,
        POSTGRES_SCHEMA: 'O2P',
        TABLESPACE_MAP: {},
        '_pls2pgs': {
            ":OLD.": "OLD.",
            ":NEW.": "NEW.",
            "INSERTING": "TG_OP = 'INSERT'",
            "UPDATING": "TG_OP = 'UPDATE'",
            "DELETING": "TG_OP = 'DELETE'",
            " NUMBER": " NUMERIC",
            " PLS_INTEGER": " INTEGER",
            " VARCHAR2": " VARCHAR",
            'RAISE_APPLICATION_ERROR': 'CALL RAISE_APPLICATION_ERROR',
            "SQL%ROWCOUNT": "sql_rowcount()"
        },
        '_target_path_validated': False
    }

    specified_parameters = {k: v for k, v in kwargs.items() if not k.startswith('_')}
    if specified_parameters:
        parameters.update(**specified_parameters)

    return parameters


# -----------------------------------------------

# Ignoring pylint issues with _output_type_handler, as arguments are defined by cx_Oracle.
# pylint: disable=invalid-name, too-many-arguments, unused-argument

def _output_type_handler(cursor, name, defaultType, size, precision, scale):        # noqa
    """
    Converts Clob to Long to improve performance.
    Parameter names and order are specified by cx_Oracle
    """

    if defaultType == cx_Oracle.CLOB:
        return cursor.var(cx_Oracle.LONG_STRING, arraysize=cursor.arraysize)
    if defaultType == cx_Oracle.BLOB:
        return cursor.var(cx_Oracle.LONG_BINARY, arraysize=cursor.arraysize)
    return None


# -----------------------------------------------
# End.
