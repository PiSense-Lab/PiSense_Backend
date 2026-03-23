from fastapi import APIRouter, Dapends, status
from pisense.backend.models.table_models import DataTable
from pisense.backend.classes import Database

router = APIRouter(prefix="/datapoints")

@router.post("/add_datapoint")
async def add_datapoint(
        time: str | None = None
        value: int | None = None
):
    time = time
