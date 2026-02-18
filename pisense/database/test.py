from typing import List
import mariadb
from fastapi import FastAPI, Form, HTTPException
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

ALLOWED_TYPES = {"INT", "VARCHAR(50)", "TEXT", "DATE", "TIME"}

def valid_identifier(name):
    return bool(re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', name))

#Create a new table from input from front end. Expects form data with 'table_name', 'column_name[]', and 'column_type[]'

def create_table(
    table_name: str = "test",
    column_name: List[str] = ["id", "name", "value"],
    column_type: List[str] = ["INT", "VARCHAR(50)", "TEXT"]
):
    # Validate table name
    if not valid_identifier(table_name):
        raise HTTPException(status_code=400, detail="Invalid table name")

    #Validate each column has a type and vice versa
    if len(column_name) != len(column_type):
        raise HTTPException(status_code=400, detail="Each column must have a type and vice versa")

    column_defs = []

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

create_table()