from contextlib import asynccontextmanager
import logging
from pisense.backend.classes import Database, Authenticator
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
from pisense.backend.routes.weather import router as weather_router
from pisense.backend.routes.datasheets import router as tables_router
from pisense.backend.routes.user import router as user_router


# to start server: source .venv/bin/activate && fastapi dev pisense/api/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    Database()# Sets up database connection singleton

    Authenticator() # Sets up Authenticator

    yield # Run the api

    # Shutdown Code
    logging.info("Api Has Been Shutdown")

app = FastAPI(lifespan=lifespan)

origins = [
    "*" # Remove for production and replace with prod url
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Adjust for security in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather_router)
app.include_router(tables_router)
app.include_router(user_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
