from fastapi import APIRouter, File, UploadFile, status, HTTPException
from io import BytesIO
import pandas as pd
import json
from datetime import time
from typing import Any, List
from typing import List
from pisense.backend.classes import Database
from pisense.backend.models.table_models import DataTable


router = APIRouter(prefix="/datatables")


# make it return the row numbers and the tablenames
#   of all the tables in a project
@router.get("/")
async def read_tables(project_id: int | None = None):
    db = Database()

    if project_id is None:
        res = db.get_table(project_id=None)  # or define a clearer "get_all"
    else:
        res = db.get_table(project_id=project_id)

    return res

@router.get("/{table_name}", response_model=DataTable)
async def read_single_table(
    table_name: str,
    project_id: int | None = None
):
    db = Database()

    res = db.get_table(table_name=table_name, project_id=project_id)

    return {"data": res}

@router.post("/get_rows", response_model=DataTable)
async def get_rows(
    table: str,
    columns: List[str] | None = None,
    where_condition: str = ""
):
    db = Database()
    res = db._get_rows(table, columns, where_condition)

    return {"data": res}

@router.get("/get_users", response_model=DataTable)
async def get_users(
    username: str | None = None,
):
    db = Database()
    res = db.get_users(username=username)
    return {"data": res.to_dict(orient="records")}

@router.get("/get_projects", response_model=DataTable)
async def get_projects(
    name: str | None = None,
    owner: str | None = None,
):
    db = Database()
    res = db.get_projects(name=name, owner=owner)
    return {"data": res.to_dict(orient="records")}

@router.get("/get_project", response_model=DataTable)
async def get_project(
    project_id: int,
    name: str | None = None,
):
    db = Database()
    res = db.get_project(project_id, name=name)
    return {"data": res.to_dict(orient="records")}

@router.get("/get_user_projects", response_model=DataTable)
async def get_user_projects(
    id: int | None = None,
):
    db = Database()
    res = db.get_user_projects(id)
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
        row_data: List[List[Any]],
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

@router.patch("/add_column", status_code=200)
async def add_column(
        column_name: List[str],
        column_type: List[str],
        table_name: str
):
    db = Database()
    db._add_column(table_name, column_name, column_type)

@router.patch("/delete_column", status_code=200)
async def delete_column(
        table_name: str,
        column_name: List[str],
):
    db = Database()
    db._delete_column(table_name, column_name)

@router.patch("/rename_column", status_code=200)
async def rename_column(
        table_name: str,
        old_column_name: str,
        new_column_name: str
):
    db = Database()
    db.rename_column(table_name,old_column_name,new_column_name)

@router.post("/create_table", status_code=200)
async def create_table(
        table_name: str,
        column_name: List[str],
        column_type: List[str],
        project_id: int | None = None
):
    db = Database()
    db.create_table(table_name, column_name, column_type,project_id)
    return {"table_name": table_name}

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
@router.post("/upload_excel/", status_code=200)
async def upload_excel_file(
        project_id: int | None,
        file: UploadFile = File(...)
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
    db.df_create_table(file.filename.replace(".xlsx", ""), df)

    # Process the DataFrame (e.g., convert to JSON or perform analysis)
    # Returning a dictionary, which FastAPI serializes to JSON
    return {
        "filename": file.filename,
        "rows": len(df),
        "columns": len(df.columns),
        # You can return the data in JSON format for the client
        "data_sample": df.head().to_dict(orient="records")
    }

    