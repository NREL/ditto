
# Remove this import since it works only for Windows...
# import win32com.client
#
# Use Pandas_access instead
import pandas_access as mdb

import pandas as pd
import os


class DbParser:
    """
    Class implementing the reading of the MDB tables used by Synergi.
    """

    def __init__(self, input_file):
        """
        Class constructor.
        """
        self.SynergiDictionary = {}
        self.paths = {}
        self.paths["Synergi File"] = input_file
        self.ParseSynergiDatabase()

    def ParseSynergiDatabase(self):
        """
        Use Pandas Access to convert the MDB tables to Pandas DataFrames.
        """
        print("Opening synergie database - ", self.paths["Synergi File"])
        table_list = mdb.list_tables(self.paths["Synergi File"])
        for table in table_list:
            self.SynergiDictionary[table] = mdb.read_table(
                self.paths["Synergi File"], table
            )
        return

    # def __ParseSynergiDatabase_deprecated(self, dataFile):
    #     """
    #     This only works on Windows.
    #     Deprecated.
    #     """
    #     print("Opening synergie database - ", self.__Paths["Synergi File"])
    #     databaseFile = os.getcwd() + "\\" + dataFile
    #     connectionString = (
    #         "Driver={Microsoft Access Driver (*.mdb, *.accdb)};Dbq=%s" % databaseFile
    #     )
    #     dbConnection = pyodbc.connect(connectionString)
    #     cursor = dbConnection.cursor()
    #     TableInfo = [[list(row)[2], list(row)[3]] for row in cursor.tables()]
    #     for TableName, TableType in TableInfo:
    #         if TableType.lower() == "table":
    #             print("Parsing table - ", TableName)
    #             sql = "select * from " + TableName
    #             data = pd.read_sql(sql, dbConnection)
    #             self.SynergiDictionary[TableName] = data
    #     cursor.close()
    #     dbConnection.close()
    #     return
