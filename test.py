from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv
from pisense.backend.classes import Database

from fastapi import FastAPI

ENV_FILE_PATH = ".env" # root of the repository

# Startup code
load_dotenv(dotenv_path=ENV_FILE_PATH) # Loads .env file into environment

# Access environment variables using os.getenv
db_password = os.getenv("MARIADB_PASSWORD")
username = os.getenv("MARIADB_USER")
host = os.getenv("HOST")

db = Database(db_password=db_password,username=username,host=host) # Sets up database connection singleton

db._add_column("test", ["number", "city"], ["INT", "VARCHAR(50)"])