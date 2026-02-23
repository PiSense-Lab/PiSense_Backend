
import re
from typing import List

from mariadb import Cursor, Connection, mariadb
import logging
import sys
from fastapi import HTTPException

def validate_value(value, col_type):
    col_type = col_type.upper()

    if col_type == "INT":
        try:
            int(value)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Value {value} is not an INT")
    elif col_type == "DECIMAL":
        try:
            float(value)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Value {value} is not a DECIMAL")
    elif col_type.startswith("VARCHAR"):
        max_len = int(col_type[col_type.find("(")+1 : col_type.find(")")])
        if len(str(value)) > max_len:
            raise HTTPException(status_code=400, detail=f"Value {value} exceeds max length {max_len}")
    elif col_type == "DATE":
        import datetime
        try:
            datetime.datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Value {value} is not a valid DATE")
    elif col_type == "TIME":
        import datetime
        try:
            datetime.datetime.strptime(value, "%H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Value {value} is not a valid TIME")
    elif col_type == "BOOL":
        try:
            bool(value)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Value {value} is not a valid BOOLEAN")

def valid_identifier(name):
    return bool(re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', name))

class Group():

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"{self.name}"

    @property
    def users(self) -> list["User"]:
        """
        Returns a list of users that are a part of this group

        :return: list of users that are a part of this group
        :rtype: list[User]
        """
        ...

    @property
    def projects(self) -> list["Project"]:
        """
        Returns a list of projects owned by this object

        :return: list of projects owned by this object
        :rtype: list[Project]
        """
        ...

class User():

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"{self.name}"

    @property
    def projects(self) -> list["Project"]:
        """
        Returns a list of projects owned by this object

        :return: list of projects owned by this object
        :rtype: list[Project]
        """
        ...

class Project():

    def __init__(self, name: str, owner: User | Group):
        self.name = name
        self.owner = owner

    def __str__(self):
        return f"{self.name}"

    @property
    def users(self) -> list["User"]:
        """list of users that can access this project"""
        ...

class Database():
    """
    Connection object to the database.
    """

    _cursor: Cursor
    _connection: Connection
    _instance: "Database" = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs) -> "Database": # Singleton implementation, returns existing instance if it exists
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_password: str = "", host: str = "", username: str = "admin", port: int = 3306, database: str = "PiSense"):
        # Connect to db -> _connection
        if self._initialized:
            return
        self._initialized = True
        try:
            self._connection = mariadb.connect(
                user=username,
                password=db_password,
                host=host,
                port=port,
                database=database,
                connect_timeout=10,
                read_timeout=10,
                write_timeout=10
            )
            if not isinstance(self._connection, Connection):
                logging.error("Did not return a connection object")
                sys.exit(1)
        except mariadb.Error as e:
            logging.error(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

        # create cursor -> _cursor
        self._cursor: Cursor = self._connection.cursor()

    @property
    def cursor(self) -> Cursor:
        if not isinstance(self._cursor, Cursor):
            logging.error("Did not return a connection object")
            sys.exit(1)
        return self._cursor

    @property
    def connection(self) -> Connection:
        return self._connection()
    
    def _get_rows(self, table: str, columns: List[str] = [], where_condition: str = "") -> list[tuple]:

        # Validate table name
        if not valid_identifier(table):
            raise HTTPException(status_code=400, detail="Invalid table name")

        # Validate column names
        for col in columns:
            if not valid_identifier(col.strip()):
                raise HTTPException(status_code=400, detail=f"Invalid column name: {col}")
            
        cols = "*"
        if columns:
            cols = ", ".join(col.strip() for col in columns)

        
        where = ""
        if where_condition:
            where = f" WHERE {where_condition}"


        sql_str = f"SELECT {cols} FROM PiSense.{table}{where}"
    
        self.cursor.execute(sql_str)

        out = self.cursor.fetchall()

        if isinstance(out, List):
            return out
        else:
            raise Exception("SQL did not return a list")

    def get_groups(self) -> list[Group]:
        """
        Returns a list of Groups

        :return: List of Groups
        :rtype: list[Group]
        """
        ...

    def get_users(self) -> list[User]:
        """
        Returns a list of users.

        :return: List of users.
        :rtype: list[User]
        """
        ...

    def get_projects(self, owner: User | Group | None = None) -> list[Project]:
        """
        Returns a list of projects. Returns all projects if owner is None otherwise only return projects owned by owner

        :return: List of projects.
        :rtype: list[Project]
        """

        ...

    def get_group(self) -> Group:
        """
        Returns a group from the database

        :return: Group from the database
        :rtype: Project
        """
        ...

    def get_project(self) -> Project:
        """
        Returns a project from the database

        :return: Project from the database
        :rtype: Project
        """
        ...

    def get_user(self) -> User:
        """
        Returns a user from the database

        :return: User from the database
        :rtype: User
        """
        ...

    def get_table(self):
        """
        Returns a table from the database

        :return: Table from the database.
        :rtype: ??? ( Make a table object? )
        """
        ...

    def create_table(self):
        """
        Creates a table in the database
        """
        ...

    def create_project(self):
        """
        Creates a new project in the database.
        """
        ...

    def create_user(self):
        """
        Creates a new user in the database.
        """
        ...

    def create_group(self):
        """
        Creates a new group in the database.
        """
        ...