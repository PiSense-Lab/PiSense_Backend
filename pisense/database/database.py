from mariadb import Cursor, Connection

from pisense.backend.classes import Group, User, Project

class Database():
    """
    Docstring for database
    """

    _cursor: Cursor | None = None
    _connection: Connection | None = None


    def __init__():
        # Connect to db -> _connection
        # create cursor -> _cursor
        ...

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


        # .env file
    

