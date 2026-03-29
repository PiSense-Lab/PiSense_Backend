from fastapi import APIRouter, File, UploadFile, status, HTTPException
from io import BytesIO
import pandas as pd
import json
from datetime import time
from typing import Annotated, List
from pisense.backend.classes import Database
from pisense.backend.models.table_models import DataTable


router = APIRouter(prefix="/datatables")

# make it return the row numbers and the tablenames
#   of all the tables in a project
@router.get("")
async def read_tables(
        project_id: int | None
):
    db =  Database()
    if project_id is None:
        res = db.get_table()
    else:
        res = db.get_table(project_id=project_id)

    return {"root": res.to_dict(orient="records")}

@router.get("/{table_name}", response_model=DataTable)
async def read_single_table(
        table_name: str,
        project_id: int | None = None
):
    db = Database()

    if project_id is None:
        res = db.get_table(table_name)
    else:
        res = db.get_table(table_name, project_id)

    return {"data": res.to_dict(orient="records")}

@router.patch("/edit_point", status_code=200)
async def edit_point(
        row_num: int,
        row_data: List[int | float],
        row_columns: List[str],
        table_name: str
):
    db = Database()
    db.modify_row(table_name, row_num, row_data=row_data, row_columns=row_columns, mode="edit")

@router.patch("/add_point", status_code=200)
async def add_point(
        row_data: List[List[int | float | time]],
        row_columns: List[str],
        table_name: str
):
    db = Database()
    db._insert_rows(table_name, row_columns, row_data)

@router.patch("/remove_point", status_code=200)
async def remove_point(
        row_num: int,
        table_name: str
):
    db = Database()
    db.modify_row(table_name, row_num,mode="delete")


@router.post("/upload_manual", status_code=200)
async def upload_manual(
        json_in: str,
        table_name: str
):
    db = Database()
    df = pd.DataFrame(json.loads(json_in))
    db.df_create_table(table_name, df)  # come back to for project_id
    return {"table_name": table_name, "json": json_in}

@router.post("/upload_csv/")
async def upload_csv(
        table_name: str | None,
        project_id: int | None,
        file: UploadFile = File(...),
):
    db = Database()
    df = pd.read_csv(BytesIO(await file.read()))
    if table_name is None:
        table_name = file.filename
    db.df_create_table(table_name, df)  # come back to for project_id
    return {"filename": file.filename, "rows_count": len(df)}

# originally generated with AI
@router.post("/upload_excel/", status_code=201)
async def upload_excel_file(
        project_id: int | None,
        file: Annotated[UploadFile, File(...)],
):
    """
    Receives an Excel file and processes it using pandas.
    """
    if file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload an Excel file (.xlsx)."
        )

    # Read the file content into memory
    content = await file.read()

    # Use BytesIO to create a file-like object for pandas
    try:
        # df is not a dataframe it is a dict of dataframes
        df = pd.read_excel(BytesIO(content), engine='openpyxl')
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error processing Excel file: {e}"
        )

    db = Database()

    for key, value in df:
        db.df_create_table(key, value)

    # Process the DataFrame (e.g., convert to JSON or perform analysis)
    # Returning a dictionary, which FastAPI serializes to JSON
    return {
        "filename": file.filename,
        "rows": len(df),
        "columns": len(df.columns),
        # You can return the data in JSON format for the client
        "data_sample": df.head().to_dict(orient="records")
    }
