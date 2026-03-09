from fastapi import APIRouter, Depends
from pisense.backend.classes import Database
from pisense.backend.models.table_models import DataTable


router = APIRouter(prefix="/datatables")

@router.get("", response_model=list[DataTable])
async def read_tables():
    db =  Depends(Database())
    res = db.get_table()

    return res

@router.get("/{tablename}")
async def read_single_table(
        tablename: str
        ):
    db =  Depends(Database())
    res = db.get_table(tablename)

    return res

# @router.post("/upload_file", status_code=201)
# async def upload_file():
#     db = Depends(Database())
#     res =
