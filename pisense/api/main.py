from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv
from pisense.database.database import Database

from fastapi import FastAPI

ENV_FILE_PATH = ".env" # root of the repository


db: Database


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db
    # Startup code
    load_dotenv(dotenv_path=ENV_FILE_PATH) # Loads .env file into environment

    # Access environment variables using os.getenv
    db_password = os.getenv("MARIADB_PASSWORD")
    username = os.getenv("MARIADB_USER")
    host = os.getenv("HOST")

    db = Database(db_password=db_password,username=username,host=host) # Sets up database connection

    yield # Run the api
    
    # Shutdown Code
    logging.info("Api Has Been Shutdown")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    print(db)
    return {"message": "Hello World"}
