from fastapi import APIRouter, Depends
import pandas as pd
from pisense.backend.classes import Database
from pisense.backend.models.table_models import DataTable

router = APIRouter(prefix="/testing")


#for testing purposes 
@router.post("/upload")
async def test_upload(
        project_name: str | None,
        tablename: str
):
    db = Database()
    df = pd.read_csv("./tests/ExampleData.csv")
    db.create_project(project_name)
    db.df_create_table(tablename, df)

    return f"Table created with project: {project_name}, and tablename: {tablename}"
