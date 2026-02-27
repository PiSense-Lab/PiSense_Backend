from datetime import datetime
from fastapi import HTTPException, APIRouter, Depends
from pisense.backend.models.table_models import DataTable

router = APIRouter(prefix="/datatables")

@router.get("", response_model=List[?])
def read_tables():
    
    return 

@router.get("/{tableID}")
def read_single_table():

    return 


@router.post("")
