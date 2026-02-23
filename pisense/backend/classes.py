
from mariadb import Cursor, Connection, mariadb
import logging
import sys
from pisense.backend.classes import Group, User, Project

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
            self._connection: Connection = mariadb.connect(
                user=username,
                password=db_password,
                host=host,
                port=port,
                database=database,
                connect_timeout=10,
                read_timeout=10,
                write_timeout=10
            )
        except mariadb.Error as e:
            logging.error(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

        # create cursor -> _cursor
        self._cursor = self._connection.cursor()

    @property
    def cursor(self):
        return self._cursor

    @property
    def connection(self):
        return self._connection()

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

class Project():

    def __init__(self, name: str, owner: "User" | "Group"):
        self.name = name
        self.owner = owner

    def __str__(self):
        return f"{self.name}"

    @property
    def users(self) -> list["User"]:
        """list of users that can access this project"""
        ...

class Group():

    def __init__(self):
        ...

    def __str__(self):
        ...

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

    @property
    def name(self) -> str:
        """
        Returns name of object

        :return: name of object
        :rtype: str
        """
        ...

class User():

    def __init__(self, name: str):
        ...

    def __str__(self):
        ...

    @property
    def projects(self) -> list["Project"]:
        """
        Returns a list of projects owned by this object

        :return: list of projects owned by this object
        :rtype: list[Project]
        """
        ...

    @property
    def name(self) -> str:
        """
        Returns name of object

        :return: name of object
        :rtype: str
        """
        ...
