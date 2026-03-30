import  pandas as pd
import re
from typing import List, Literal
from enum import Enum

from mariadb import Connection, mariadb
from sqlalchemy import create_engine, text
import logging
import sys
from fastapi import HTTPException
from pisense.backend.exceptions import DatabaseError
from pisense.database.validate import validate_value
def database_to_user(user: tuple) -> "User":
    #["id", "username", "firstname", "lastname", "role", "email"]
    return User(id=int(user[0]), username=str(user[1]), firstname=str(user[2]), lastname=str(user[3]), role=str(user[4]), email=str(user[5]))

def database_to_project(project: tuple) -> "Project":
    return Project(id=int(project[0]), name=str(project[1]), description=str(project[2]), public=bool(project[3]), archived=bool(project[4]))

class ValidationError(Exception):
    pass

def valid_identifier(name):
    return bool(re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', name))

class USER_ROLES(Enum):
    admin = 1
    analyst = 2
    viewer = 3

class User():

    def __init__(self, id: int, role: str, username: str, email: str, firstname: str, lastname: str):
        self.id = id
        self.role = USER_ROLES[role]
        self.username = username
        self.email = email
        self.firstname = firstname
        self.lastname = lastname

    def __str__(self):
        return f"({self.id}, {self.username}, {self.role}, {self.email}, {self.firstname}, {self.lastname})"

    # @property
    # def projects(self) -> list["Project"]:
    #     """
    #     Returns a list of projects owned by this object

    #     Gets information from `user_projects` table

    #     :return: list of projects owned by this object
    #     :rtype: list[Project]
    #     """
    #     sql_cmd = []
    #     db = Database()
    #     projects = db.get_user_projects()

# CREATE TABLE projects (
#     project_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
#     project_name VARCHAR(100) NOT NULL,
#     description TEXT DEFAULT NULL,
#     public TINYINT(1) DEFAULT NULL,
#     archived TINYINT(1) DEFAULT NULL
# );

class Project():

    def __init__(self, id: int, name: str, description: str, public: bool, archived: bool ):
        #owner: User | Group
        self.id = id
        self.name = name
        self.description = description
        self.public = public
        self.archived = archived
        #self.owner = owner

    def __str__(self):
        return f"({self.id}, {self.name}, `{self.description}`, public: {self.public}, archived: {self.archived})"

    # @property
    # def users(self) -> list["User"]:
    #     """list of users that can access this project"""
    #     ...

class Database():
    """
    Connection object to the database.
    """

    # _cursor: Cursor
    _connection: Connection
    _instance: "Database" = None
    _initialized: bool = False

    ALLOWED_TYPES = {"INT", "VARCHAR(50)", "BOOL", "DATE", "TIME", "FLOAT"}

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

            engine = create_engine(
                    f"mariadb+mariadbconnector://{username}:{db_password}@{host}:{port}/{database}"
                    )
            self._connection = engine.connect()
        except mariadb.Error as e:
            logging.error(f"Host: {host} Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

        # create cursor -> _cursor
        # self._cursor: Cursor = self._connection.cursor()

    # @property
    # def cursor(self) -> Cursor:
    #    if not isinstance(self._cursor, Cursor):
    #        logging.error("Did not return a connection object")
    #        sys.exit(1)
    #    return self._cursor

    @property
    def connection(self) -> Connection:
        return self._connection

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

        res = self._connection.execute(text(sql_str))

        out = res.fetchall()

        if isinstance(out, List):
            return out
        else:
            raise Exception("SQL did not return a list")

    def _insert_rows(self, table_name: str, column_name: List[str], rows: List[List[str]]):
        """
        Inserts rows into given table.
        """
        # Validate table name
        if not valid_identifier(table_name):
            raise HTTPException(status_code=400, detail="Invalid table name")

        # Validate column names
        for col in column_name:
            if not valid_identifier(col.strip()):
                raise HTTPException(status_code=400, detail=f"Invalid column name: {col}")

        # Fetch column types from the existing table
        res = self._connection.execute(text(f"DESCRIBE {table_name}"))
        schema = {col[0]: col[1].upper() for col in res.fetchall()}  # {column_name: column_type}

        # Make sure all columns exist
        for col in column_name:
            if col not in schema:
                raise HTTPException(status_code=400, detail=f"Column {col} does not exist in table {table_name}")

        cols = ", ".join(col.strip() for col in column_name)
        placeholders = ", ".join([f":{col}" for col in column_name])
        cols = cols.replace("index", "`index`")
        cols = cols.replace("DateTime", "`DateTime`")
        query = text(f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})")

        # Insert rows
        for row in rows:
            if len(row) != len(column_name):
                raise HTTPException(status_code=400, detail="Row length does not match column length")

            # Validate each value against its column type
            for val, col in zip(row, column_name):
                validate_value(val, schema[col])


            d_rows = dict(zip(column_name, row))
            self.connection.execute(query, d_rows)    #safe parameter binding

        self.connection.commit()
        return f"{len(rows)} rows inserted!"

    def _add_column(self, table_name: str, column_name: List[str], column_type: List[str]):
        """
        Adds column(s) to existing table
        """
        # Validate table name
        if not valid_identifier(table_name):
            raise HTTPException(status_code=400, detail="Invalid table name")

        # Validate column names
        for col in column_name:
            if not valid_identifier(col.strip()):
                raise HTTPException(status_code=400, detail=f"Invalid column name: {col}")

        #Validate each column has a type and vice versa
        if len(column_name) != len(column_type):
            raise HTTPException(status_code=400, detail="Each column must have a type and vice versa")

        column_defs = []
        for c, t in zip(column_name, column_type):
            c = c.strip()
            t = t.strip().upper()

            #validates column name
            if not valid_identifier(c):
                raise HTTPException(status_code=400, detail=f"Invalid column name: {c}")

            #validates allowed types
            if t not in self.ALLOWED_TYPES:
                raise HTTPException(status_code=400, detail=f"Invalid type: {t}")

            #Adds valid column definition to list
            column_defs.append(f"ADD COLUMN `{c}` {t}")

        #Checks if there are valid columns to create the table with
        if not column_defs:
            raise HTTPException(status_code=400, detail="No valid columns")

        query = f"ALTER TABLE `{table_name}` {', '.join(column_defs)}"

        print("success!")
        self.cursor.execute(query)
        self.connection.commit()

        return "Column Added!"

    def _alter_data(self, table_name: str, column_name: List[str], row: List[List[str]]):
        """
        Edits data in existing row
        """

        # Validate table name
        if not valid_identifier(table_name):
            raise HTTPException(status_code=400, detail="Invalid table name")

        # Validate column names
        for col in column_name:
            if not valid_identifier(col.strip()):
                raise HTTPException(status_code=400, detail=f"Invalid column name: {col}")

        # Fetch column types from the existing table
        self.cursor.execute(f"DESCRIBE {table_name}")
        schema = {col[0]: col[1].upper() for col in self.cursor.fetchall()}

        # Make sure all columns exist
        for col in column_name:
            if col not in schema:
                raise HTTPException(
                    status_code=400,
                    detail=f"Column {col} does not exist in table {table_name}"
                )

        # Validate row structure
        for r in row:
            if len(r) != len(column_name) + 1:   # +1 for row id
                raise HTTPException(
                    status_code=400,
                    detail="Row length must match columns + row id"
                )

        # Validate values
        for r in row:
            for col, value in zip(column_name, r[:-1]):
                col_type = schema[col]
                validate_value(value, col_type)

        # Build update query
        set_clause = ", ".join([f"{col} = %s" for col in column_name])
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"

        # Execute updates
        for r in row:
            values = r[:-1]
            row_id = r[-1]

            self.cursor.execute(query, (*values, row_id))

            self.connection.commit()

        return {"message": "Rows updated successfully"}

    def register_dataset(self, project_id: int, table_name: str):
        """
        Link an existing table to a project by inserting it into the dataset table.
        """
        # Validate table name
        if not valid_identifier(table_name):
            raise ValueError("Invalid table name")

        # Make sure project exists
        self.cursor.execute("SELECT project_id FROM projects WHERE project_id = %s", (project_id,))
        if not self.cursor.fetchone():
            raise ValueError(f"Project with ID {project_id} does not exist")

        # Optional: check if the table is already registered
        self.cursor.execute("SELECT dataset_id FROM dataset WHERE table_name = %s AND project_id = %s",
                            (table_name, project_id))
        if self.cursor.fetchone():
            raise ValueError(f"Table '{table_name}' is already linked to project {project_id}")

        # Insert into dataset
        self.cursor.execute(
            "INSERT INTO dataset (project_id, table_name) VALUES (%s, %s)",
            (project_id, table_name)
        )
        self.connection.commit()

        return {"message": f"Table '{table_name}' linked to project {project_id} successfully"}

    def get_users(self, username: str | None = None) -> list[User]:
        """
        Returns a list of users.

        :return: List of users.
        :rtype: list[User]
        """
        where = []
        where_condition = ""
        if username:
            where.append(f"username LIKE '%{username}%'")

        if len(where) > 0:
            where_condition = f"{where[0]}"
            if len(where) > 1:
                for w in range(1, len(where)):
                    where_condition = f"{where_condition} AND {where[w]}"

        ret = []
        users = self._get_rows("users", ["id", "username", "firstname", "lastname", "role", "email"], where_condition=where_condition)
        for u in users:
            ret.append(database_to_user(u))
        return ret

    def get_projects(self, name: str | None = None) -> list[Project]:
        """
        Returns a list of projects. Returns all projects if owner is None otherwise only return projects owned by owner

        :return: List of projects.
        :rtype: list[Project]
        """
        where = []
        where_condition = ""
        if name:
            where.append(f"project_name LIKE '%{name}%'")

        if len(where) > 0:
            where_condition = f"{where[0]}"
            if len(where) > 1:
                for w in range(1, len(where)):
                    where_condition = f"{where_condition} AND {where[w]}"

        ret = []
        projects = self._get_rows("projects", ["project_id", "project_name", "description", "public", "archived"], where_condition=where_condition)
        for p in projects:
            ret.append(database_to_project(p))
        return ret

    def get_project(self, id: int | None = None, name: str | None = None) -> Project:
        """
        Returns a project from the database

        :return: Project from the database
        :rtype: Project
        """
        where = []
        where_condition = ""
        if id:
            where.append(f"project_id = {id}")
        if name:
            where.append(f"project_name = '{name}'")

        if len(where) > 0:
            where_condition = f"{where[0]}"
            if len(where) > 1:
                for w in range(1, len(where)):
                    where_condition = f"{where_condition} AND {where[w]}"
        else:
            raise DatabaseError("No Where condition set, please set a parameter,")

        users = self._get_rows("projects", ["project_id", "project_name", "description", "public", "archived"], where_condition=where_condition)

        if len(users) == 0:
            raise DatabaseError("No project found.")
        if len(users) > 1:
            raise DatabaseError("More than one project found, tighten constraints or use `get_projects` function.")

        return database_to_user(users[0])

    def get_user(self, id: int | None = None, username: str | None = None) -> User:
        """
        Returns a user from the database

        Will add conditions together with AND

        :return: User from the database
        :rtype: User
        """
        where = []
        where_condition = ""
        if id:
            where.append(f"id = {id}")
        if username:
            where.append(f"username = '{username}'")

        if len(where) > 0:
            where_condition = f"{where[0]}"
            if len(where) > 1:
                for w in range(1, len(where)):
                    where_condition = f"{where_condition} AND {where[w]}"
        else:
            raise DatabaseError("No Where condition set, please set a parameter,")

        users = self._get_rows("users", ["id", "username", "firstname", "lastname", "role", "email"], where_condition=where_condition)

        if len(users) == 0:
            raise DatabaseError("No user found.")
        if len(users) > 1:
            raise DatabaseError("More than one user found, tighten constraints or use `get_users` function.")

        return database_to_user(users[0])

    def get_user_projects(self, user_id: int):
        return self._get_rows("user_projects", ["user_id", "project_id", "role_id"], where_condition=f"user_id = {user_id}")

    def get_table(self, table_name: str | None = None, project_id: int | None = None):
        """
        Returns a table from the database

        :return: Table from the database.
        :rtype: pd.DataFrame ( Make a table object? )
        """
        if not valid_identifier(table_name):
            raise HTTPException(status_code=400, detail="Invalid table name")


        if project_id and table_name:
            query = f"SELECT * FROM {table_name} WHERE project_id={project_id}"

        if table_name is not None and project_id is None:
            query = table_name

        if table_name is None and project_id is not None:
            query = f"SELECT * WHERE project_id={project_id}"



        raw_df = pd.read_sql_table(query, con=self.connection)


        if len(raw_df) == 0:
            raise DatabaseError("No table found")
        # if len(raw_df) > 1:
        #    raise DatabaseError(f"More than one table found with tablename: {table_name}")

        return raw_df

    def create_table(self, table_name: str, column_name: List[str], column_type: List[str], project_id: int):
        """
        Creates a table in the database
        """
        # Validate table name
        if not valid_identifier(table_name):
            raise HTTPException(status_code=400, detail="Invalid table name")

        #Validate each column has a type and vice versa
        if len(column_name) != len(column_type):
            raise HTTPException(status_code=400, detail="Each column must have a type and vice versa")

        column_defs = []

        column_defs.append("id INT PRIMARY KEY AUTO_INCREMENT")

        #removes whitespace and capitalizes
        for c, t in zip(column_name, column_type):
            c = c.strip()
            t = t.strip().upper()

            #validates column name
            if not valid_identifier(c):
                raise HTTPException(status_code=400, detail=f"Invalid column name: {c}")

            #validates allowed types
            if t not in self.ALLOWED_TYPES:
                raise HTTPException(status_code=400, detail=f"Invalid type: {t}")

            #Adds valid column definition to list
            column_defs.append(f"{c} {t}")

        #Checks if there are valid columns to create the table with
        if not column_defs:
            raise HTTPException(status_code=400, detail="No valid columns")

        #Joins column definitions into a string for the SQL query
        cols = ", ".join(column_defs)

        query = f"CREATE TABLE {table_name} ({cols})"

        self._connection.execute(text(query))
        print("Table success!")

        #Creates dataset row to connect project to the table
        self.register_dataset(project_id, table_name)

        self.connection.commit()

        return "Table created!"

    def df_create_table(
            self,
            table_name: str | None = None,
            df: pd.DataFrame | None = None,
    ):
        if df is None or not isinstance(df, pd.DataFrame):
            raise HTTPException(status_code=400, detail="Not a pandas DataFrame")

        if not valid_identifier(table_name):
            raise HTTPException(status_code=400, detail="Table name is not valid")


        #for col_name in df.columns:
#
#            if not valid_identifier(col_name):
#                raise HTTPException(status_code=400, detail=f"Invalid column name: {col_name}")

        try:
            # if the table exists it will fail with a ValueError
            df.to_sql(table_name, self.connection, schema="PiSense", if_exists="fail")
            # self._connection.execute(text(""))
        except Exception as e:
            print(f"Error: {e}")

        return "Table created!"

    def modify_row(
            self,
            table_name: str,
            row_num: int,
            row_data: List[str] | None,
            row_columns: List[str] | None,
            mode: Literal["edit", "delete"]
    ):
        if not valid_identifier(table_name):
            raise HTTPException(status_code=400, detail="Table name is not valid")

        # Validate column names
        for col in row_columns:
            if not valid_identifier(col.strip()):
                raise HTTPException(status_code=400, detail=f"Invalid column name: {col}")

        # Fetch column types from the existing table
        res = self._connection.execute(text(f"DESCRIBE {table_name}"))
        schema = {col[0]: col[1].upper() for col in res.fetchall()}  # {column_name: column_type}

        # Make sure all columns exist
        for col in row_columns:
            if col not in schema:
                raise HTTPException(status_code=400, detail=f"Column {col} does not exist in table {table_name}")


        if mode == "edit":
            if row_data is not None and row_columns is not None:
                query = f"UPDATE {table_name} SET " # WHERE index={row_num}"

                # for col, data in zip(row_columns, row_data):
                e_query = ", ".join(f"{col} = {data}" for col, data in zip(row_columns, row_data))
                query += e_query
                query += f" WHERE `index`={row_num}"

                return_msg = f"Row in {table_name} updated to {row_data}"

            else:
                raise HTTPException(status_code=400, detail="No row or column data")

        if mode == "delete":
            query = f"DELETE FROM {table_name} WHERE index={row_num}"

            return_msg = f"Row in {table_name} at {row_num} deleted"


        self.connection.execute(text(query))
        self.connection.commit()

        return return_msg


    def create_project(self, 
                       name: str,
                       description: str = "",
                       public: bool = False,
                       archived: bool = False
                       ):
        """
        Creates a new project in the database.'

        TODO: Return created project.
        """
        columns = ["project_name"]
        output = [f"{name}"]

        if not isinstance(description, type(None)):
            columns.append("description")
            output.append(description)

        if not isinstance(public, type(None)):
            columns.append("public")
            output.append(public)

        if not isinstance(archived, type(None)):
            columns.append("archived")
            output.append(archived)

        print(f"column: {columns}")
        print(f"output: {output}")

        self._insert_rows("projects", columns, [output])

    def create_user(self,
                    username: str,
                    role: USER_ROLES,
                    email: str | None = None,
                    password: str | None = None,
                    firstname: str | None = None,
                    lastname: str | None = None
                    ):
        """
        Creates a new user in the database.
        """
        columns = ["username", "role"]
        output = [f"{username}", str(role.name)]

        if not isinstance(email, type(None)):
            columns.append("email")
            output.append(email)

        if not isinstance(password, type(None)):
            columns.append("password")
            output.append(password)

        if not isinstance(firstname, type(None)):
            columns.append("firstname")
            output.append(firstname)

        if not isinstance(lastname, type(None)):
            columns.append("lastname")
            output.append(lastname)

        self._insert_rows("users", columns, [output])
