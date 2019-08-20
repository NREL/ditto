# Remove this import since it works only for Windows...
# import win32com.client
import os
import pandas as pd
import subprocess
import re
import numpy as np


class DbParser:
    """
    Class implementing the reading of the MDB tables used by Synergi.
    """

    def __init__(self, input_file, **kwargs):
        """
        Class constructor.
        """
        self.SynergiDictionary = {}
        self.paths = {}
        self.paths["Synergi File"] = input_file
        self.current_dir = os.path.realpath(os.path.dirname(__file__))
        self.path_to_mdbtools = os.path.join(self.current_dir, "mdbtools/bin/")
        self.TABLE_RE = re.compile(
            "CREATE TABLE \[(\w+)\]\s+\((.*?\));", re.MULTILINE | re.DOTALL
        )

        self.DEF_RE = re.compile("\s*\[(\w+)\]\s*(.*?),")

        if "warehouse" in kwargs:
            self.paths["warehouse"] = kwargs["warehouse"]

        self.ParseSynergiDatabase()

    # Using all the functions from the package, pandas_access and editing the path to the downloaded mdbtools path.

    def list_tables(self, rdb_file, encoding="latin-1"):
        """
        :param rdb_file: The MS Access database file.
        :param encoding: The content encoding of the output. I assume `latin-1`
        because so many of MS files have that encoding. But, MDBTools may
        actually be UTF-8.
        :return: A list of the tables in a given database.
        """
        tables = subprocess.check_output(
            [os.path.join(self.path_to_mdbtools, "mdb-tables"), rdb_file]
        ).decode(encoding)
        return tables.strip().split(" ")

    def _extract_dtype(self, data_type):
        # Note, this list is surely incomplete. But, I only had one .mdb file
        # at the time of creation. If you see a new data-type, patch-pull or just
        # open an issue.
        data_type = data_type.lower()
        if data_type.startswith("double"):
            return np.float_
        elif data_type.startswith("long"):
            return np.int_
        else:
            return None

    def _extract_defs(self, defs_str):
        defs = {}
        lines = defs_str.splitlines()
        for line in lines:
            m = self.DEF_RE.match(line)
            if m:
                defs[m.group(1)] = m.group(2)
        return defs

    def read_schema(self, rdb_file, encoding="utf8"):
        """
        :param rdb_file: The MS Access database file.
        :param encoding: The schema encoding. I'm almost positive that MDBTools
            spits out UTF-8, exclusively.
        :return: a dictionary of table -> column -> access_data_type
        """
        output = subprocess.check_output(
            [os.path.join(self.path_to_mdbtools, "mdb-schema"), rdb_file]
        )
        lines = output.decode(encoding).splitlines()
        schema_ddl = "\n".join(l for l in lines if l and not l.startswith("-"))

        schema = {}
        for table, defs in self.TABLE_RE.findall(schema_ddl):
            schema[table] = self._extract_defs(defs)

        return schema

    def to_pandas_schema(self, schema, implicit_string=True):
        """
        :param schema: the output of `read_schema`
        :param implicit_string: mark strings and unknown dtypes as `np.str_`.
        :return: a dictionary of table -> column -> np.dtype
        """
        pd_schema = {}
        for tbl, defs in schema.items():
            pd_schema[tbl] = None
            sub_schema = {}
            for column, data_type in defs.items():
                dtype = self._extract_dtype(data_type)
                if dtype is not None:
                    sub_schema[column] = dtype
                elif implicit_string:
                    sub_schema[column] = np.str_
            pd_schema[tbl] = sub_schema
        return pd_schema

    def read_table(self, rdb_file, table_name, *args, **kwargs):
        """
        Read a MS Access database as a Pandas DataFrame.
        Unless you set `converters_from_schema=False`, this function assumes you
        want to infer the schema from the Access database's schema. This sets the
        `dtype` argument of `read_csv`, which makes things much faster, in most
        cases. If you set the `dtype` keyword argument also, it overrides
        inferences. The `schema_encoding keyword argument passes through to
        `read_schema`. The `implicit_string` argument passes through to
        `to_pandas_schema`.
        I recommend setting `chunksize=k`, where k is some reasonable number of
        rows. This is a simple interface, that doesn't do basic things like
        counting the number of rows ahead of time. You may inadvertently start
        reading a 100TB file into memory. (Although, being a MS product, I assume
        the Access format breaks after 2^32 bytes -- har, har.)
        :param rdb_file: The MS Access database file.
        :param table_name: The name of the table to process.
        :param args: positional arguments passed to `pd.read_csv`
        :param kwargs: keyword arguments passed to `pd.read_csv`
        :return: a pandas `DataFrame` (or, `TextFileReader` if you set
            `chunksize=k`)
        """
        if kwargs.pop("converters_from_schema", True):
            specified_dtypes = kwargs.pop("dtype", {})
            schema_encoding = kwargs.pop("schema_encoding", "utf8")
            schemas = self.to_pandas_schema(
                self.read_schema(rdb_file, schema_encoding),
                kwargs.pop("implicit_string", True),
            )
            dtypes = schemas[table_name]
            dtypes.update(specified_dtypes)
            if dtypes != {}:
                kwargs["dtype"] = dtypes
        cmd = [os.path.join(self.path_to_mdbtools, "mdb-export"), rdb_file, table_name]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        return pd.read_csv(proc.stdout, *args, **kwargs)

    def ParseSynergiDatabase(self):
        """
        Use Pandas Access to convert the MDB tables to Pandas DataFrames.
        """
        print("Opening synergie database - ", self.paths["Synergi File"])
        table_list = self.list_tables(self.paths["Synergi File"])

        table_list_warehouse = []
        if "warehouse" in self.paths:
            print("Opening warehouse database - ", self.paths["warehouse"])
            table_list_warehouse = self.list_tables(self.paths["warehouse"])

        for table in table_list:
            self.SynergiDictionary[table] = self.ToLowerCase(
                self.read_table(self.paths["Synergi File"], table)
            )

        for table in table_list_warehouse:
            self.SynergiDictionary[table] = self.ToLowerCase(
                self.read_table(self.paths["warehouse"], table)
            )
        return

    def ToLowerCase(self, df):
        """
        This function converts all the input data to lower case.
        """
        df = df.apply(lambda x: x.str.lower() if x.dtype == "object" else x)
        return df
