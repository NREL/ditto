# Remove this import since it works only for Windows...
# import win32com.client
import pandas as pd
import os

from . import pandas_access as mdb


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

        if "warehouse" in kwargs:
            self.paths["warehouse"] = kwargs["warehouse"]

        self.ParseSynergiDatabase()

    def ParseSynergiDatabase(self):
        """
        Use Pandas Access to convert the MDB tables to Pandas DataFrames.
        """
        print("Opening synergie database - ", self.paths["Synergi File"])
        table_list = mdb.list_tables(self.paths["Synergi File"])

        table_list_warehouse = []
        if "warehouse" in self.paths:
            print("Opening warehouse database - ", self.paths["warehouse"])
            table_list_warehouse = mdb.list_tables(self.paths["warehouse"])

        for table in table_list:
            self.SynergiDictionary[table] = self.ToLowerCase(
                mdb.read_table(self.paths["Synergi File"], table)
            )

        for table in table_list_warehouse:
            self.SynergiDictionary[table] = self.ToLowerCase(
                mdb.read_table(self.paths["warehouse"], table)
            )
        return

    def ToLowerCase(self, df):
        """
        This function converts all the input data to lower case.
        """
        df = df.apply(lambda x: x.str.lower() if x.dtype == "object" else x)
        return df
