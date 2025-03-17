import sqlite3
from lib.logs import Log  # class Log from logs.py

class SqliteDAO:
    # """SQLite3 Data Access Object provides API to work with SQLite3 Database"""

    def __init__(self, dbLocation: str = None):
        try:
            if dbLocation is not None:
                self.__dbLocation = dbLocation
                self.__conn = None
                self.__logger = Log(__name__)
            else:
                print("Need database location!")
        except sqlite3.Error as error:
            self.__logger.exception(error)
            print("Init database failed!")

    def __connect__(self):
        try:
            self.__conn = sqlite3.connect(self.__dbLocation)
            self.__conn.cursor().execute("PRAGMA foreign_keys = ON;")
        except sqlite3.Error as error:
            self.__logger.exception(error)
            print("Connect database failed!")

    def __do__(self, query: str, params=None) -> list[tuple]:
        try:
            self.__connect__()
            cur = self.__conn.cursor()
            if (params):
                cur.execute(query, params)
            else:
                cur.execute(query)
            values = cur.fetchall()
            self.__close__()
            return values
        except sqlite3.Error as error:
            self.__logger.exception(error)
            #print(f"Do {query} failed!")
            print(error)
    # brief: method to close a connection to sqlite3
    #

    def __close__(self):
        try:
            self.__conn.commit()
            self.__conn.cursor().close()
            self.__conn.close()
        except sqlite3.Error as error:
            self.__logger.exception(error)
            print("Close database failed!")

    # TODO: change print to log file
    # brief: method to create a table in sqlite3
    #       1. open a connection to a database
    #       2. execute the command "Create a table" in that database
    #       3. log the message to logger
    #       4. close the connection afterward
    def createTable(self, tableName: str, colName: str):
        try:
            self.__connect__()
            cur = self.__conn.cursor()
            cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tableName}';")
            result = cur.fetchone()
            if result is None:
                self.__do__(f"CREATE TABLE {tableName} ({colName});")
                print(f"CREATE TABLE {tableName} successfully")
                self.__logger.info(
                    f"Created table {tableName} successfully")
            else:
                print(f"{tableName} already exists in the database.")
        except sqlite3.Error as error:
            self.__logger.info("Created table {tableName} unsuccessfully")
            self.__logger.exception(error)

    # brief: method to insert a record to a tableName
    #       1. open a connection to a database
    #       2. execute the command "Insert data to table" in that database
    #       3. log the message to logger
    #       4. close the connection afterward

    def insertOneRecord(self, tableName: str, colName: list[str], colValues: tuple[float]):
        try:
            placeHolder = ", ".join(["?" for _ in range(len(colName))])
            colName = ", ".join(colName)
            self.__do__(
                f"INSERT INTO {tableName} ({colName}) VALUES ({placeHolder})", colValues)
            print(f"Insert {colValues} in {tableName} table")
        except sqlite3.Error as error:
            self.__logger.exception(error)
            #print(error)

    # brief: method to retrieve all tables that are currently available in database
    #       1. open a connection to a database
    #       2. execute the command "SELECT name FROM sqlite_master WHERE type='table';" in that database
    #       3. log the message to logger
    #       4. close the connection afterward
    def listAllTables(self) -> list:
        # """Show all tables in database"""
        try:
            items = self.__do__(
                "SELECT name FROM sqlite_master WHERE type='table';")
            return [table[0] for table in items]
        except sqlite3.Error as error:
            self.__logger.exception(error)
            print(error)

    def listAllColumns(self, tableName) -> list:
        try:
            items = self.__do__(f"PRAGMA table_info({tableName});")
            return [column[0] for column in items]
        except sqlite3.Error as error:
            self.__logger.exception(error)
            print(error)

    def listAllValues(self, tableName) -> list:
        try:
            items = self.__do__(f"PRAGMA table_info({tableName});")
            return [item[0] for item in items]
        except sqlite3.Error as error:
            self.__logger.exception(error)
            print(error)

    def listAllValuesInColumn(self, tableName, columnName) -> list:
        try:
            items = self.__do__(f"SELECT {columnName} FROM {tableName};")
            return [item[0] for item in items]
        except sqlite3.Error as error:
            self.__logger.exception(error)
            print(error)

    # # DISCLAIMED: These functions have not been tested
    # # UPDATE
    # # TODO: use rowid
    # def updateOneRecord(self, tableName, new, condition):
    #     try:
    #         self.__connect__()
    #         self.__do__(f"UPDATE {tableName} SET {new} WHERE {condition}")
    #         self.__logger.info("Updated a record successfully")
    #     except sqlite3.Error as error:
    #         self.__logger.info("Updated a record unsuccessfully")
    #         self.__logger.exception(error)
    #     finally:
    #         self.__close__()

    # # DELETE
    # def deleteOneRecord(self, tableName, condition):
    #     try:
    #         self.__connect__()
    #         self.__do__(f"DELETE FROM {tableName} WHERE {condition}")
    #         self.__logger.info("Deleted a record successfully")
    #     except sqlite3.Error as error:
    #         self.__logger.info("Deleted a record unsuccessfully")
    #         self.__logger.exception(error)
    #     finally:
    #         self.__close__()


if __name__ == "__main__":
    pass
