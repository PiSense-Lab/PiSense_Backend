from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv
from pisense.backend.classes import Database
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
from pisense.backend.routes.weather import router as weather_router
from pisense.backend.routes.datasheets import router as tables_router


ENV_FILE_PATH = ".env" # root of the repository

# to start server: source .venv/bin/activate && fastapi dev pisense/api/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    ENV_FILE_PATH = ".env" # root of the repository

    # Startup code
    load_dotenv(dotenv_path=ENV_FILE_PATH) # Loads .env file into environment

    # Access environment variables using os.getenv
    db_password = os.getenv("MARIADB_PASSWORD")
    username = os.getenv("MARIADB_USER")
    host = os.getenv("MARIADB_HOST")

    Database(db_password=db_password, host=host, username=username)# Sets up database connection singleton

    yield # Run the api

    # Shutdown Code
    logging.info("Api Has Been Shutdown")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust for security in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather_router)
app.include_router(tables_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
