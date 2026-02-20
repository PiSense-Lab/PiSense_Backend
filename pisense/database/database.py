from mariadb import Cursor, Connection, mariadb
import logging
import sys
from pisense.backend.classes import Group, User, Project

class Database():
    """
    Docstring for database
    """

    _cursor: Cursor
    _connection: Connection

    def __init__(self, db_password: str, host: str, username: str = "admin", port: int = 3306, database: str = "PiSense"):
        # Connect to db -> _connection
        try:
            self._connection: Connection = mariadb.connect(
                user=username,
                password=db_password,
                host=host,
                port=port,
                database=database
            )
        except mariadb.Error as e:
            logging.error(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

        # create cursor -> _cursor
        self._cursor = self._connection.cursor()
    @property
    def cursor(self):
        return self._cursor
    
    def get_groups(self) -> list[Group]:
        ...

    def get_users(self) -> list[User]:
        ...

    def get_projects(self) -> list[Project]:
        ...

    def get_group(self) -> Group:
        ...

    def get_project(self) -> Project:
        ...

    def get_user(self) -> User:
        ...

    def get_table(self):
        ...

    
    def create_table():
        ...

    def create_project():
        ...

    def create_user():
        ...

    def create_group():
        ...
