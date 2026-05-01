
from pisense.backend.classes import Database
from fastapi import APIRouter


router = APIRouter(prefix="/utility")

@router.get("/reconnect")
async def reconnect_to_db():
    """
    Runs the reconnect function for the database

    """
    ran = Database()._connect_to_db()

    if ran:
        message = "Database Reconnected"
    else:
        message = "Database was Connected"

    return { "message": message, "ran": ran }
