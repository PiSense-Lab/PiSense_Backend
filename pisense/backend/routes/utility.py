from pisense.backend.classes import Database
from pisense.backend.exceptions import DatabaseError
from fastapi import APIRouter, HTTPException
from fastapi import status

router = APIRouter(prefix="/utility")

@router.get("/reconnect")
async def reconnect_to_db():
    """
    Runs the reconnect function for the database

    returns:
        (str): message
        (bool): ran
    """
    try:
        ran = Database()._connect_to_db()
        if ran:
            message = "Database Reconnected"
        else:
            message = "Database was Connected"
    except DatabaseError as e:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unhandled Exception: {e}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return { "message": message, "ran": ran }
