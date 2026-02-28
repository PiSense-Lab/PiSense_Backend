from typing import List
import mariadb
from pisense.database.validate import validate_value
from fastapi import HTTPException
import sys
import re

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="admin",
        password="",
        host="192.168.1.90",
        port=3306,
        database="PiSense"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

ALLOWED_TYPES = {"INT", "VARCHAR(50)", "BOOL", "DATE", "TIME"}

def valid_identifier(name):
    return bool(re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', name))

#Create a new table from input from front end. Expects form data with 'table_name', 'column_name[]', and 'column_type[]'

def create_table(
    table_name: str = "test2",
    column_name: List[str] = ["name", "value"],
    column_type: List[str] = ["VARCHAR(50)", "INT"]
):
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
        if t not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail=f"Invalid type: {t}")

        #Adds valid column definition to list
        column_defs.append(f"{c} {t}")

    #Checks if there are valid columns to create the table with
    if not column_defs:
        raise HTTPException(status_code=400, detail="No valid columns")

    #Joins column definitions into a string for the SQL query
    cols = ", ".join(column_defs)

    query = f"CREATE TABLE {table_name} ({cols})"

    print("success!")
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()

    return "Table created!"

def insert_rows(table_name: str, column_name: List[str], rows: List[List[str]]):
    # Validate table name
    if not valid_identifier(table_name):
        raise HTTPException(status_code=400, detail="Invalid table name")

    # Validate column names
    for col in column_name:
        if not valid_identifier(col.strip()):
            raise HTTPException(status_code=400, detail=f"Invalid column name: {col}")

    # Fetch column types from the existing table
    cur = conn.cursor()
    cur.execute(f"DESCRIBE {table_name}")
    schema = {col[0]: col[1].upper() for col in cur.fetchall()}  # {column_name: column_type}

    # Make sure all columns exist
    for col in column_name:
        if col not in schema:
            raise HTTPException(status_code=400, detail=f"Column {col} does not exist in table {table_name}")

    cols = ", ".join(col.strip() for col in column_name)
    placeholders = ", ".join(["?"] * len(column_name))
    query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

    # Insert rows
    for row in rows:
        if len(row) != len(column_name):
            raise HTTPException(status_code=400, detail="Row length does not match column length")

        # Validate each value against its column type
        for val, col in zip(row, column_name):
            validate_value(val, schema[col])

        cur.execute(query, row)  # safe parameter binding

    conn.commit()
    return f"{len(rows)} rows inserted!"
