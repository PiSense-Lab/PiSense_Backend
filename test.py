from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv
from pisense.backend.classes import Database

from fastapi import FastAPI
from pisense.backend.classes import USER_ROLES

ENV_FILE_PATH = ".env" # root of the repository

# Startup code
load_dotenv(dotenv_path=ENV_FILE_PATH) # Loads .env file into environment

# Access environment variables using os.getenv
db_password = os.getenv("MARIADB_PASSWORD")
username = os.getenv("MARIADB_USER")
host = os.getenv("MARIADB_HOST")

db = Database(db_password=db_password,username=username,host=host) # Sets up database connection singleton


username = "test_username_admin2"
# db.create_user(username, USER_ROLES.admin)
# users = db._get_rows("users", where_condition=f"username='{username}'")
user = db.get_users()
print(user)

# table_name = "survey_results_test"
# column_name = ["age", "city", "score"]
# column_type = ["INT", "VARCHAR(50)", "FLOAT"]
# project_id = 10   # your example project

# db.create_table(table_name, column_name, column_type, project_id)