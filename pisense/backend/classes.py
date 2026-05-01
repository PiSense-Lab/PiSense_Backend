from datetime import date, datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
import mariadb
from pandas import col
from passlib.context import CryptContext

import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Annotated,  Union
from pydantic import Field
from jose import JWTError, jwt
import  pandas as pd
import re
from typing import Any, Dict, List, Literal, Tuple
from enum import Enum

from sqlalchemy import Boolean, Column, Integer, MetaData, String, Text, create_engine, text, Connection, insert, Table
from sqlalchemy import Enum as Enum_sql
import logging
import sys
from fastapi import Depends, HTTPException
import sqlalchemy
from pisense.backend.exceptions import CouldNotConnectToDBError, DatabaseError, DatabaseReconnectingError, FindingRowError, UnauthorizedUserError
from pisense.database.validate import validate_value

def valid_existing_identifier(name: str) -> bool:
    """Looser check for column names that already exist in the DB (allows spaces)."""
    return bool(re.match(r'^[A-Za-z_][A-Za-z0-9_ ]*$', name))

def quote_identifier(name: str) -> str:
    """Wraps a column/table name in backticks, escaping internal backticks."""
    return "`" + name.replace("`", "``") + "`"

class AddColumnChange(BaseModel):
    type: Literal["add_column"]
    table_name: str
    column_name: List[str]
    column_type: List[str]

class RenameColumnChange(BaseModel):
    type: Literal["rename_column"]
    table_name: str
    old_column_name: str
    new_column_name: str

class DeleteColumnChange(BaseModel):
    type: Literal["delete_column"]
    table_name: str
    column_name: List[str]

class EditRowChange(BaseModel):
    type: Literal["edit_row"]
    table_name: str
    row_num: int
    row_data: List[str]
    row_columns: List[str]

class DeleteRowChange(BaseModel):
    type: Literal["delete_row"]
    table_name: str
    row_num: int

class InsertRowsChange(BaseModel):
    type: Literal["insert_rows"]
    table_name: str
    column_name: List[str]
    rows: List[List[str]]

Change = Annotated[
    Union[
        AddColumnChange,
        RenameColumnChange,
        DeleteColumnChange,
        EditRowChange,
        DeleteRowChange,
        InsertRowsChange,
    ],
    Field(discriminator="type")
]


class ApplyChangesRequest(BaseModel):
    changes: List[Change]


def database_to_user(user: dict) -> "User":
    return User(
        id=int(user["id"]),
        username=str(user["username"]),
        firstname=str(user["firstname"]),
        lastname=str(user["lastname"]),
        email=str(user["email"]),
        hashed_password=str(user["password"])
    )

def database_to_project(project: dict, database: "Database") -> "Project":
    users = database.get_user_projects(project_id=project["project_id"])
    owner_id = None
    for u in users:
        if u["role"] == USER_ROLES.admin.name:
            owner_id = u["user_id"]
            break

    if not owner_id:
        raise DatabaseError(f"Could not find valid owner for project {project['project_id']} | {project['project_name']}")

    return Project(
        id=int(project["project_id"]),
        name=str(project["project_name"]),
        description=str(project["description"]),
        public=bool(project["public"]),
        archived=bool(project["archived"]),
        last_updated=(project["last_updated"]),
        owner_id=owner_id
    )

def database_user_project_to_dict( user_project: tuple ) -> dict:
    return {
        "user_projects_id": user_project[0],
        "user_id": user_project[1],
        "project_id": user_project[2],
        "role": user_project[3],
    }

def user_dict_to_user( u: dict ) -> "User":
    return User(id=u["id"], username=u["username"], email=u["email"], firstname=u["firstname"], lastname=u["lastname"], hashed_password=u['password'])

class ValidationError(Exception):
    pass

def valid_identifier(name):
    return bool(re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', name))

class USER_ROLES(str, Enum):
    admin = 1
    analyst = 2
    viewer = 3



class User():

    def __init__(self, id: int, username: str, email: str, firstname: str, lastname: str, hashed_password: str):
        self.id = id
        self.username = username
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.hashed_password = hashed_password

    def __str__(self):
        return f"({self.id}, {self.username}, {self.email}, {self.firstname}, {self.lastname})"


    # def set_password():
    #     ...

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

class Project():

    def __init__(self, id: int, name: str, description: str, public: bool, archived: bool, owner_id: User, last_updated: date):
        self.id = id
        self.name = name
        self.description = description
        self.public = public
        self.archived = archived
        self.last_updated = last_updated
        self.owner_id = owner_id

    @property
    def owner(self) -> User:
        ...
        # Get owner from self.owner_id

    def __str__(self):
        return f"({self.id}, {self.name}, `{self.description}`, public: {self.public}, archived: {self.archived}, last_updated: {self.last_updated})"

    @property
    def users(self) -> list[dict]:
        """list of users that can access this project and their permission

        ret: [ { "user": user, { "user": user2, "role": USER_ROLE } ]
        """
        users = []
        user_projects = Database().get_user_projects(project_id=self.id)
        for up in user_projects:
            user = Database().get_user(up['user_id'])
            users.append({ "user": user, "role": USER_ROLES[up['role']] })
        return users

    def add_user(self, user_id: int, role: USER_ROLES):
        for up in self.users:
            if up["user"].id == user_id:
                raise DatabaseError("User is already in database.")

        Database().create_user_projects(user_id, self.id, role)


class Database():
    """
    Connection object to the database.
    """

    # _cursor: Cursor
    connection: Connection
    _instance: "Database" = None
    _initialized: bool = False

    ALLOWED_TYPES = {"INT", "VARCHAR(50)", "BOOL", "DATE", "TIME", "FLOAT"}


    def _connect_to_db(self, force: bool = False) -> bool:
        """ Reconnects to db if ping fails, will return true if it did a reconnection, false if ping passed"""
        run = False
        if force:
            run = True
        else:
            try:
                self.connection.execute(text("SELECT 1"))
            except ( mariadb.InterfaceError, sqlalchemy.exc.InterfaceError ):
                run = True
            except ( sqlalchemy.exc.OperationalError ) as e:
                self.connection.rollback()
                raise CouldNotConnectToDBError("Could not ping database ip, could be a network related issue.") from e

        if run:
            print("Connecting to database")
            load_dotenv(dotenv_path=".env")

            db_password = os.getenv("MARIADB_PASSWORD")
            host = os.getenv("MARIADB_HOST")
            username = os.getenv("MARIADB_USER", "admin")
            port = os.getenv("MARIADB_PORT", 3306)
            database = os.getenv("MARIADB_DATABASE", "PiSense")

            try:
                engine = create_engine(
                        f"mariadb+mariadbconnector://{username}:{db_password}@{host}:{port}/{database}"
                        )
                self.connection = engine.connect()
            except DatabaseError as e:
                logging.error(f"Host: {host} Error connecting to MariaDB Platform: {e}")
                sys.exit(1)

        return run

    def __new__(cls, *args, **kwargs) -> "Database": # Singleton implementation, returns existing instance if it exists
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Connect to db -> connection
        if self._initialized:
            return
        self._initialized = True

        self._connect_to_db(force=True)

        self.metadata = MetaData()
        self.users_table = Table(
                            "users",
                            self.metadata,
                            Column("id", Integer, primary_key=True, autoincrement=True, nullable=False),
                            #Column("role", Enum_sql("admin", "analyst", "viewer")),
                            Column("username", String(50), unique=True, default=None),
                            Column("email", String(100), default=None),
                            Column("password", String(255), unique=True, default=None),
                            Column("firstname", String(50), default=None),
                            Column("lastname", String(50), default=None),
                        )

        self.projects_table = Table(
                                "projects",
                                self.metadata,
                                Column("project_id", Integer, primary_key=True, autoincrement=True, nullable=False),
                                Column("project_name", String(100), nullable=False),
                                Column("description", Text, default=None),
                                Column("public", Boolean, default=None),
                                Column("archived", Boolean, default=None),
                            )

        self.user_projects_table = Table(
                                "user_projects",
                                self.metadata,
                                Column("user_projects_id", Integer, primary_key=True, autoincrement=True, nullable=False),
                                Column("user_id", Integer, default=None),
                                Column("project_id", Integer, default=None),
                                Column("role", Enum_sql("admin", "analyst", "viewer")),
                            )


    def apply_changes(self, changes: List[dict]) -> List[dict]:
        results = []

        DISPATCH = {
            "add_column":    lambda c: self._add_column(
                                c["table_name"], c["column_name"], c["column_type"], commit=False),
            "rename_column": lambda c: self.rename_column(
                                c["table_name"], c["old_column_name"], c["new_column_name"], commit=False),
            "delete_column": lambda c: self._delete_column(
                                c["table_name"], c["column_name"], commit=False),
            "edit_row":      lambda c: self.modify_row(
                                c["table_name"], c["row_num"], c["row_data"],
                                c["row_columns"], mode="edit", commit=False),
            "delete_row":    lambda c: self.modify_row(
                                c["table_name"], c["row_num"], None,
                                None, mode="delete", commit=False),
            "insert_rows":   lambda c: self._insert_rows(
                                c["table_name"], c["column_name"], c["rows"], commit=False),
        }

        try:
            for i, change in enumerate(changes):
                change_type = change.get("type")
                if change_type not in DISPATCH:
                    raise ValueError(f"Unknown change type: '{change_type}'")

                result = DISPATCH[change_type](change)
                results.append({"index": i, "type": change_type, "result": result})

            self.connection.commit()
            return results

        except (HTTPException, DatabaseError, ValueError) as e:
            self.connection.rollback()
            error_msg = e.detail if isinstance(e, HTTPException) else str(e)
            results.append({"index": i, "type": change_type, "error": error_msg})
            raise DatabaseError(
                f"Change #{i} ('{change_type}') failed: {error_msg}. "
                f"All changes rolled back."
            ) from e



    def update_last_updated(self, table_name: str):
        now = date.today()

        try:
            # Update dataset table
            self.connection.execute(
                text("""
                    UPDATE dataset
                    SET last_updated = :now
                    WHERE table_name = :table_name
                """),
                {"now": now, "table_name": table_name}
            )

            # Get project_id
            result = self.connection.execute(
                text("""
                    SELECT project_id FROM dataset
                    WHERE table_name = :table_name
                """),
                {"table_name": table_name}
            ).fetchone()

            # Update projects table if project exists
            if result and result[0] is not None:
                project_id = result[0]

                self.connection.execute(
                    text("""
                        UPDATE projects
                        SET last_updated = :now
                        WHERE project_id = :project_id
                    """),
                    {"now": now, "project_id": project_id}
                )

            self.connection.commit()

        except Exception as e:
            self.connection.rollback()
            raise DatabaseError(f"Failed to update last_updated: {e}") from e


    def _get_rows(
        self,
        table: str,
        columns: List[str] | None = None,
        where_condition: str = ""
    ) -> List[Dict[str, Any]]:

        # Validate table name
        if not valid_identifier(table):
            raise HTTPException(status_code=400, detail="Invalid table name")

        # Validate columns
        if columns:
            for col in columns:
                if not valid_existing_identifier(col.strip()):
                    raise HTTPException(status_code=400, detail=f"Invalid column name: {col}")

        # Build SELECT clause
        cols = "*"
        if columns:
            cols = ", ".join(quote_identifier(col.strip()) for col in columns)

        # Build WHERE clause
        where = f" WHERE {where_condition}" if where_condition else ""

        sql_str = f"SELECT {cols} FROM PiSense.{table}{where}"

        try:
            result = self.connection.execute(text(sql_str))

            rows = result.fetchall()
            keys = result.keys()  # column names

        except ( mariadb.InterfaceError, sqlalchemy.exc.InterfaceError ) as e:
            self._connect_to_db()
            self.connection.rollback()
            raise DatabaseReconnectingError( "Connection to DB Lost, Reconnecting" ) from e

        if isinstance(rows, List):
            # Convert tuples → list of dicts
            return [dict(zip(keys, row)) for row in rows]
        else:
            raise DatabaseError("SQL did not return a list")

    def _insert_rows(self, table_name: str, column_name: List[str], rows: List[List[str]], commit: bool = True) -> str:
        """
        Inserts rows into given table.
        """
        # Validate table name
        if not valid_identifier(table_name):
            raise HTTPException(status_code=400, detail="Invalid table name")

        # Validate column names
        for col in column_name:
            if not valid_existing_identifier(col.strip()):
                raise HTTPException(status_code=400, detail=f"Invalid column name: {col}")

        # Fetch column types from the existing table
        res = self.connection.execute(text(f"DESCRIBE {table_name}"))
        schema = {col[0]: col[1].upper() for col in res.fetchall()}  # {column_name: column_type}

        # Make sure all columns exist
        for col in column_name:
            if col not in schema:
                raise HTTPException(status_code=400, detail=f"Column {col} does not exist in table {table_name}")

        
        cols = ", ".join(quote_identifier(col.strip()) for col in column_name)
        placeholders = ", ".join([":val" + str(i) for i in range(len(column_name))])
        query = text(f"INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders})")

        for row in rows:
            if len(row) != len(column_name):
                raise HTTPException(status_code=400, detail="Row length does not match column length")

            for val, col in zip(row, column_name):
                validate_value(val, schema[col])

            # Use positional keys: val0, val1, val2 ...
            params = {f"val{i}": v for i, v in enumerate(row)}
            self.connection.execute(query, params)

        if commit:
            self.connection.commit()
        return f"{len(rows)} rows inserted!"

    def _insert_row(self, table_name: str, key: List[str], value: List[str], commit: bool = True) -> Tuple:
        table: Table | None = None
        if table_name == "users":
            table = self.users_table

        if table_name == "projects":
            table = self.projects_table

        if table_name == "user_projects":
            table = self.user_projects_table

        if isinstance(table, type(None)):
            raise DatabaseError(f"Could not find table of type {table_name}, check spelling or implement sqlalchemy table")


        # Convert to dict, we should just pass though as dict in the first place
        row = dict(zip(key, value))

        try:
            stmt = insert(table).returning(table)
            out = self.connection.execute(stmt, [row]).fetchone()

            if commit:
                self.connection.commit()
        except Exception as e:
            raise DatabaseError(f"Error adding to database: {e}") from None # Hides very long and useless traceback

        key.insert(0,"id")
        return dict(zip(key, out))

    def _add_column(self, table_name: str, column_name: List[str], column_type: List[str], commit: bool = True):
        """
        Adds column(s) to an existing table using SQLAlchemy.
        """

        # Validate table name
        if not valid_identifier(table_name):
            raise HTTPException(status_code=400, detail="Invalid table name")

        # Validate column names
        for col in column_name:
            if not valid_identifier(col.strip()):
                raise HTTPException(status_code=400, detail=f"Invalid column name: {col}")

        # Ensure matching lengths
        if len(column_name) != len(column_type):
            raise HTTPException(status_code=400, detail="Each column must have a type and vice versa")

        column_defs = []

        for c, t in zip(column_name, column_type):
            c = c.strip()
            t = t.strip().upper()

            # Validate column name again (defensive)
            if not valid_identifier(c):
                raise HTTPException(status_code=400, detail=f"Invalid column name: {c}")

            # Validate allowed types
            if t not in self.ALLOWED_TYPES:
                raise HTTPException(status_code=400, detail=f"Invalid type: {t}")

            column_defs.append(f"ADD COLUMN `{c}` {t}")

        if not column_defs:
            raise HTTPException(status_code=400, detail="No valid columns")

        query = f"ALTER TABLE `{table_name}` {', '.join(column_defs)}"

        # Execute using SQLAlchemy
        self.connection.execute(text(query))
        if commit:
            self.connection.commit()

        return "Column Added!"

    def _alter_data(
        self,
        table_name: str,
        column_name: List[str],
        row: List[List[str]],
        commit: bool = True
    ):
        """
        Edits data in existing rows using SQLAlchemy.
        """

        # Validate table name
        if not valid_identifier(table_name):
            raise HTTPException(status_code=400, detail="Invalid table name")

        # Validate column names
        for col in column_name:
            if not valid_existing_identifier(col.strip()):
                raise HTTPException(status_code=400, detail=f"Invalid column name: {col}")

        # Fetch schema
        res = self.connection.execute(text(f"DESCRIBE `{table_name}`"))
        schema = {col[0]: col[1].upper() for col in res.fetchall()}

        # Ensure columns exist
        for col in column_name:
            if col not in schema:
                raise HTTPException(
                    status_code=400,
                    detail=f"Column {col} does not exist in table {table_name}"
                )

        # Validate row structure
        for r in row:
            if len(r) != len(column_name) + 1:  # +1 for row id
                raise HTTPException(
                    status_code=400,
                    detail="Row length must match columns + row id"
                )

        # Validate values against schema
        for r in row:
            for col, value in zip(column_name, r[:-1]):
                validate_value(value, schema[col])

        set_clause = ", ".join([f"{quote_identifier(col)} = :{col}" for col in column_name])
        query = text(f"UPDATE {quote_identifier(table_name)} SET {set_clause} WHERE {quote_identifier('index')} = :row_id")

        # Execute updates
        for r in row:
            values = r[:-1]
            row_id = r[-1]

            params = dict(zip(column_name, values))
            params["row_id"] = row_id

            self.connection.execute(query, params)

        if commit:
            self.connection.commit()

        return {"message": "Rows updated successfully"}

    def rename_column(self, table_name: str, old_column_name: str, new_column_name: str, commit: bool = True):
        if not valid_identifier(table_name):
            raise HTTPException(status_code=400, detail="Invalid table name")
        if not valid_existing_identifier(old_column_name):
            raise HTTPException(status_code=400, detail="Invalid old column name")
        if not valid_identifier(new_column_name):
            raise HTTPException(status_code=400, detail="Invalid new column name")

        res = self.connection.execute(text(f"DESCRIBE `{table_name}`"))
        schema_rows = res.fetchall()
        schema = {
            col[0]: {
                "type": col[1],
                "null": col[2],
                "default": col[4],
                "extra": col[5] or "",
            }
            for col in schema_rows
        }

        if old_column_name not in schema:
            raise HTTPException(status_code=400, detail=f"Column {old_column_name} does not exist in table {table_name}")
        if new_column_name in schema:
            raise HTTPException(status_code=400, detail=f"Column {new_column_name} already exists in table {table_name}")
        col_info = schema[old_column_name]
        null_clause = "NOT NULL" if col_info["null"] == "NO" else "NULL"
        default_clause = ""
        if col_info["default"] is not None:
            default_value = col_info["default"]
            default_clause = f"DEFAULT '{default_value}'" if isinstance(default_value, str) else f"DEFAULT {default_value}"
        query = text(
            f"ALTER TABLE `{table_name}` "
            f"CHANGE `{old_column_name}` `{new_column_name}` "
            f"{col_info['type']} {null_clause} {default_clause} {col_info['extra']}".strip()
        )

        self.connection.execute(query)
        if commit:
            self.connection.commit()
        return f"Column '{old_column_name}' renamed to '{new_column_name}' in table '{table_name}'"

    def _delete_column(self, table_name: str, column_name: List[str], commit: bool = True):
        """
        Deletes column(s) from existing table
        """
        # Validate table name
        if not valid_identifier(table_name):
            raise HTTPException(status_code=400, detail="Invalid table name")
        # Validate column names
        for col in column_name:
            if not valid_identifier(col.strip()):
                raise HTTPException(status_code=400, detail=f"Invalid column name: {col}")

        # Fetch existing columns
        res = self.connection.execute(text(f"DESCRIBE `{table_name}`"))
        existing_columns = {col[0] for col in res.fetchall()}

        # Check if columns exist
        for col in column_name:
            if col not in existing_columns:
                raise HTTPException(status_code=400, detail=f"Column {col} does not exist in table {table_name}")

        # Build drop queries
        drop_clauses = [f"DROP COLUMN `{col.strip()}`" for col in column_name]
        query = f"ALTER TABLE `{table_name}` {', '.join(drop_clauses)}"

        self.connection.execute(text(query))
        if commit:
            self.connection.commit()
        return f"Column(s) {', '.join(column_name)} deleted from table {table_name}"

    def register_dataset(self, project_id: int, table_name: str):
        """
        Link an existing table to a project by inserting it into the dataset table.
        """

        # Validate table name
        if not valid_identifier(table_name):
            raise ValueError("Invalid table name")

        # Check if project exists
        res = self.connection.execute(
            text("SELECT project_id FROM projects WHERE project_id = :pid"),
            {"pid": project_id}
        )

        if not res.fetchone():
            raise ValueError(f"Project with ID {project_id} does not exist")

        # Check if already registered
        res = self.connection.execute(
            text("""
                SELECT dataset_id
                FROM dataset
                WHERE table_name = :tname AND project_id = :pid
            """),
            {"tname": table_name, "pid": project_id}
        )

        if res.fetchone():
            raise ValueError(f"Table '{table_name}' is already linked to project {project_id}")

        # Insert into dataset
        self.connection.execute(
            text("""
                INSERT INTO dataset (project_id, table_name)
                VALUES (:pid, :tname)
            """),
            {"pid": project_id, "tname": table_name}
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
        users = self._get_rows("users", ["id", "username", "firstname", "lastname", "email", "password"], where_condition=where_condition)
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
        projects = self._get_rows("projects", ["project_id", "project_name", "description", "public", "archived", "last_updated"], where_condition=where_condition)
        for p in projects:
            ret.append(database_to_project(p, self))
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

        projects = self._get_rows("projects", ["project_id", "project_name", "description", "public", "archived", "last_updated"], where_condition=where_condition)

        if len(projects) == 0:
            raise DatabaseError("No project found.")
        if len(projects) > 1:
            raise DatabaseError("More than one project found, tighten constraints or use `get_projects` function.")

        return database_to_project(projects[0], self)

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

        try:
            users = self._get_rows("users", ["id", "username", "firstname", "lastname", "email", "password"], where_condition=where_condition)
        except ( DatabaseReconnectingError, DatabaseError ) as e:
            raise e
        except FindingRowError as e:
            raise e


        if len(users) == 0:
            raise FindingRowError("No user found.")
        if len(users) > 1:
            raise FindingRowError("More than one user found, tighten constraints or use `get_users` function.")

        return database_to_user(users[0])

    def get_user_projects(self, user_id: int | None = None, project_id : int | None = None, role: str | None = None) -> list[dict]:
        where = []
        where_condition = ""

        if user_id:
            where.append(f"user_id = '{user_id}'")
        if project_id:
            where.append(f"project_id = '{project_id}'")
        if role:
            where.append(f"role = '{role}'")

        if len(where) > 0:
            where_condition = f"{where[0]}"
            if len(where) > 1:
                for w in range(1, len(where)):
                    where_condition = f"{where_condition} AND {where[w]}"

        return self._get_rows("user_projects", ["user_projects_id", "user_id", "project_id", "role"], where_condition=where_condition)

    def get_projects_for_user(self, user_id: int) -> list[Project]:
        user_projects = self.get_user_projects(user_id=user_id)
        return [self.get_project(id=up["project_id"]) for up in user_projects]


    def get_table(self, table_name: str | None = None, project_id: int | None = None, return_method: int | None = None):

        # -------------------------
        # CASE: both provided → validate relationship
        # -------------------------
        if table_name is not None and project_id is not None:
            if not valid_identifier(table_name):
                raise HTTPException(status_code=400, detail="Invalid table name")

            # Check mapping in dataset table
            res = self.connection.execute(
                text("""
                    SELECT 1
                    FROM dataset
                    WHERE project_id = :pid AND table_name = :tname
                    LIMIT 1
                """),
                {"pid": project_id, "tname": table_name}
            )

            if res.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Table does not belong to this project"
                )

            # If valid → fetch table
            df = pd.read_sql_query(
                f"SELECT * FROM {table_name}",
                con=self.connection
            )

            if df.empty:
                return []

            if return_method == 1:
                return df.to_dict(orient="records")

            return df

        # -------------------------
        # CASE: only table_name
        # -------------------------
        if table_name is not None:
            if not valid_identifier(table_name):
                raise HTTPException(status_code=400, detail="Invalid table name")

            df = pd.read_sql_query(
                f"SELECT * FROM {table_name}",
                con=self.connection
            )

            if df.empty:
                return []

            return df.to_dict(orient="records")

        # -------------------------
        # CASE: only project_id
        # -------------------------
        if project_id is not None:
            res = self.connection.execute(
                text("SELECT table_name FROM dataset WHERE project_id = :pid"),
                {"pid": project_id}
            )


            rows = res.fetchall()
            dataset_df = pd.DataFrame(rows, columns=["table_name"])

            if dataset_df.empty:
                raise DatabaseError("No tables found for this project")

            results = {}

            for name in dataset_df["table_name"].tolist():
                if not valid_identifier(name):
                    continue

                df = pd.read_sql_query(
                    f"SELECT * FROM {name}",
                    con=self.connection
                )

                results[name] = df.to_dict(orient="records")

            return results

        # -------------------------
        # CASE: neither provided
        # -------------------------
        raise HTTPException(status_code=400, detail="Must provide table_name or project_id")

    def get_all_tablenames(self, project_id: int):
        """
        Gets all tables from the database in a structured format
        """
        if not isinstance(project_id, int):
            raise HTTPException(status_code=400, detail="Invalid project id")

        query = text("""
            SELECT table_name, last_updated 
            FROM dataset 
            WHERE project_id = :project_id
        """)

        res = self.connection.execute(query, {"project_id": project_id})

        results = []

        for row in res:
            table = row.table_name

            # Count rows
            count_res = self.connection.execute(
                text(f"SELECT COUNT(*) FROM `{table}`")
            )
            row_count = count_res.scalar()

            # Count columns
            column_res = self.connection.execute(
                text(f"DESCRIBE `{table}`")
            )
            column_count = len(column_res.fetchall())

            results.append({
                "table_name": table,
                "last_updated": row.last_updated,
                "row_count": row_count,
                "column_count": column_count
            })

        return results

    def count_rows(self, table_name: str) -> int:
        if not valid_identifier(table_name):
            raise HTTPException(status_code=400, detail="Invalid table name")

        res = self.connection.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return res.scalar()

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


            #Creates dataset row to connect project to the table
            self.connection.execute(text(query))

            self.register_dataset(project_id, table_name)

            self.connection.commit()



            return "Table created!"

    def df_create_table(

            self,
            project_id: int | None = 1,
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
            # self.connection.execute(text(""))
        except Exception as e:
            print(f"Error: {e}")

        self.register_dataset(project_id, table_name)

        self.connection.commit()
        return "Table created!"


    def delete_table(self, table_name: str, project_id: int) -> str:
        """
        Drops a table from the database and removes its entry from the dataset table.
        Raises an error if the table is protected or doesn't belong to the given project.
        """
        PROTECTED_TABLES = {"projects", "users", "dataset", "roles", "user_projects"}

        if table_name.lower() in PROTECTED_TABLES:
            raise HTTPException(status_code=403, detail=f"Table '{table_name}' is protected and cannot be deleted")

        if not valid_identifier(table_name):
            raise HTTPException(status_code=400, detail="Invalid table name")

        # Verify the table belongs to this project
        res = self.connection.execute(
            text("""
                SELECT 1 FROM dataset
                WHERE table_name = :tname AND project_id = :pid
                LIMIT 1
            """),
            {"tname": table_name, "pid": project_id}
        )
        if res.fetchone() is None:
            raise HTTPException(status_code=404, detail="Table not found in this project")

        try:
            # Remove from dataset registry first
            self.connection.execute(
                text("DELETE FROM dataset WHERE table_name = :tname AND project_id = :pid"),
                {"tname": table_name, "pid": project_id}
            )

            # Drop the actual table
            self.connection.execute(text(f"DROP TABLE `{table_name}`"))

            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise DatabaseError(f"Failed to delete table '{table_name}': {e}") from e

        return f"Table '{table_name}' deleted successfully"

    def modify_row(
        self,
        table_name: str,
        row_num: int,
        row_data: List[str] | None,
        row_columns: List[str] | None,
        mode: Literal["edit", "delete"],
        commit: bool = True
    ):
        if not valid_identifier(table_name):
            raise HTTPException(status_code=400, detail="Table name is not valid")

        if mode == "delete":
            query = text(f"DELETE FROM {quote_identifier(table_name)} WHERE `id` = :row_id")
            self.connection.execute(query, {"row_id": row_num})  # ← bind, don't interpolate
            if commit:
                self.connection.commit()
            return f"Row in {table_name} at {row_num} deleted"

        # Everything below only runs for edit
        if row_data is None or row_columns is None:
            raise HTTPException(status_code=400, detail="No row or column data")

        for col in row_columns:
            if not valid_existing_identifier(col.strip()):
                raise HTTPException(status_code=400, detail=f"Invalid column name: {col}")

        res = self.connection.execute(text(f"DESCRIBE {table_name}"))
        schema = {col[0]: col[1].upper() for col in res.fetchall()}

        for col in row_columns:
            if col not in schema:
                raise HTTPException(status_code=400, detail=f"Column {col} does not exist in table {table_name}")

        set_clause = ", ".join(f"{quote_identifier(col)} = :{col}" for col in row_columns)
        query = text(f"UPDATE {quote_identifier(table_name)} SET {set_clause} WHERE `id` = :row_id")
        params = dict(zip(row_columns, row_data))
        params["row_id"] = row_num

        self.connection.execute(query, params)
        if commit:
            self.connection.commit()
        return f"Row in {table_name} updated to {row_data}"

    def create_user_projects(self, user_id: int, project_id: int, role: USER_ROLES ):
        columns = ["user_id", "project_id", "role"]
        output = [user_id, project_id, role.name]

        return self._insert_row("user_projects", columns, output)

    def create_project(self,
                       name: str,
                       owner_id: int,
                       description: str = "",
                       public: bool = False,
                       archived: bool = False,
                       ) -> Project:
        """
        Creates a new project in the database.
        """

        last_updated = date.today()

        columns = ["project_name", "description", "public", "archived"]
        output = [name, description, public, archived]

        project = self._insert_row("projects", columns, output)

        # Create user_projects row

        user_project = self.create_user_projects(owner_id, project["id"], USER_ROLES.admin)

        return Project(id=project["id"], name=project["project_name"], description=project["description"], public=project["public"], archived=project["archived"], owner_id=user_project["user_id"], last_updated=last_updated)

    def delete_project(self, project_id: int) -> str:
        """
        Deletes a project and all associated dataset tables and user_project rows.
        """
        PROTECTED_TABLES = {"projects", "users", "dataset", "roles", "user_projects"}

        # Check project exists
        res = self.connection.execute(
            text("SELECT 1 FROM projects WHERE project_id = :pid"),
            {"pid": project_id}
        ).fetchone()

        if res is None:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        # Get all tables linked to this project
        res = self.connection.execute(
            text("SELECT table_name FROM dataset WHERE project_id = :pid"),
            {"pid": project_id}
        ).fetchall()

        table_names = [row[0] for row in res]

        try:
            # Drop each dataset table
            for table_name in table_names:
                if not valid_identifier(table_name):
                    raise HTTPException(status_code=400, detail=f"Invalid table name: {table_name}")
                if table_name.lower() in PROTECTED_TABLES:
                    raise HTTPException(status_code=403, detail=f"Table '{table_name}' is protected and cannot be deleted")

                self.connection.execute(text(f"DROP TABLE IF EXISTS `{table_name}`"))

            # Remove all dataset rows for this project
            self.connection.execute(
                text("DELETE FROM dataset WHERE project_id = :pid"),
                {"pid": project_id}
            )

            # Remove all user_projects rows for this project
            self.connection.execute(
                text("DELETE FROM user_projects WHERE project_id = :pid"),
                {"pid": project_id}
            )

            # Finally delete the project itself
            self.connection.execute(
                text("DELETE FROM projects WHERE project_id = :pid"),
                {"pid": project_id}
            )

            self.connection.commit()

        except Exception as e:
            self.connection.rollback()
            raise DatabaseError(f"Failed to delete project {project_id}: {e}") from e

        return f"Project {project_id} and {len(table_names)} table(s) deleted successfully"

    def create_user(self,
                    username: str,
                    email: str,
                    password: str,
                    firstname: str | None = None,
                    lastname: str | None = None
                    ):
        """
        Creates a new user in the database.
        """
        print(password)
        columns = ["username", "email", "password", "firstname", "lastname"]
        output = [username, email, Authenticator().hash_password(password), firstname, lastname]

#        if firstname:
#            columns.append("firstname")
#            output.append(firstname)

#        if lastname:
#            columns.append("lastname")
#            output.append(lastname)

        try:
            user = self._insert_row("users", columns, output)
        except DatabaseError as e:
            raise e

        return user_dict_to_user(user)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Authenticator():

    _instance: "Authenticator" = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs) -> "Authenticator": # Singleton implementation, returns existing instance if it exists
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Connect to db -> connection
        if self._initialized:
            return
        self._initialized = True

        load_dotenv(dotenv_path=".env") # Loads .env file into environment

        self.SECRET_KEY: str = os.getenv("PISENSE_AUTH_SECRET_KEY")
        self.ALGORITHM: str = os.getenv("PISENSE_AUTH_ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int=os.getenv("PISENSE_AUTH_ACCESS_TOKEN_EXPIRE_MINUTES", 30)
        self.PISENSE_AUTH_ACCESS_TOKEN_REMEMBER_ME_DAYS: int=os.getenv("PISENSE_AUTH_ACCESS_TOKEN_REMEMBER_ME_DAYS", 30)

    def authenticate_user(self, username: str, password: str) -> User:
        try:
            user: User = Database().get_user(username=username)
        except FindingRowError:
            raise UnauthorizedUserError("Username was not correct")
        except DatabaseReconnectingError as e:
            raise e

        if pwd_context.verify(password, user.hashed_password):
            return user
        else:
            raise UnauthorizedUserError("Password was not correct")


    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=int(self.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def verify_token(self, token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=403, detail="Token is invalid or expired")
            return payload
        except JWTError:
            raise HTTPException(status_code=403, detail="Token is invalid or expired")

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
