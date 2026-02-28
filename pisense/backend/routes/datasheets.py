from datetime import datetime
from fastapi import HTTPException, APIRouter, Depends
from pisense.backend.models.table_models import DataTable
from pisense.backend.classes import Database
from pisense.backend.utils.dataframe_utils import toJSON, readSQL


router = APIRouter(prefix="/datatables")

@router.get("")
def read_tables(
    db = Depends(Database())
):
    res = readSQL(eng = db.connection())
    return 

@router.get("/{tablename}")
def read_single_table(
    tablename: str | None = None,
    db = Depends(Database())
):
    if tablename is not None:
        res = db.get_table(table_name=tablename)
    else:
        raise HTTPException(status_code=400, detail="Tablename cannot be None")
    
    
    return toJSON(res)
