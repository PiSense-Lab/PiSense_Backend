from sqlite3 import DatabaseError

from fastapi import APIRouter, File, UploadFile, status, HTTPException
from io import BytesIO
import pandas as pd
import json
from typing import Any, List
from pisense.backend.classes import Database
from pisense.backend.models.table_models import DataTable


router = APIRouter(prefix="/datatables")

# make it return the row numbers and the tablenames
#   of all the tables in a project
@router.get("")
async def get_tables(
        project_id: int
):
    """
    Return table metadata for all tables or for a specific project.

    params:
        project_id: ID of project to grab all table names from

    Returns: 
        (dict): root - all table names associated with project_id  
            - records styled dicts - see pandas.dataframe.to_dict

    Raises:

    """
    db =  Database()
    res = db.get_all_tablenames(project_id)

    return res

@router.get("/get_table")
async def read_single_table(
        table_name: str,
        project_id: int | None = None
):
    """
    Reads a single table from the database.

    params:
        table_name: name of table in database to be read
        project_id: Project ID of the project the table is attatched to

    Returns: 
        (dict): data - table with same name as table_name  
            - records styled dicts - see pandas.dataframe.to_dict

    Raises:

    """
    db = Database()

    if project_id is None:
        res = db.get_table(project_id=None)  # or define a clearer "get_all"
    else:
        res = db.get_table(table_name, project_id=project_id, return_method=1)

    return res


@router.post("/get_rows", response_model=DataTable)
async def get_rows(
    table: str,
    columns: List[str] | None = None,
    where_condition: str = ""
):
    """
    Retrieve rows from a single table.

    params:
        table: Name of the table to query.
        columns: Optional list of column names to return.
        where_condition: Optional SQL WHERE filter expression.

    returns:
        (DataTable): data - A DataTable response containing the requested rows.
    """
    db = Database()
    res = db._get_rows(table, columns, where_condition)

    return {"data": res}


@router.patch("/edit_table", status_code=200)
async def apply_table_changes(
    changes: List[dict],
    table_name: str
):
    """
        Applies a list of changes to the database.

    params:
    changes: List of change dictionaries, each containing:
    - action: The type of change ('edit', 'add', 'delete').
    - row_num: The row number to be modified (for 'edit' and 'delete').
    - row_data: List of values for the row (for 'edit' and 'add').
    - row_columns: List of column names corresponding to row_data (for 'edit' and 'delete').
    table_name: The name of the table to which the changes should be applied.

    Raises:
    HTTPException: If any database error occurs during the application of changes.
    """

    db = Database()
    try:
        db.apply_changes(changes)
        db.update_last_updated(table_name)

    except DatabaseError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/edit_point", status_code=200)
async def edit_point(
        row_num: int,
        row_data: List[Any],
        row_columns: List[str],
        table_name: str
):
    """
    Edits a point in a given table in the database.

    params: 
        row_num: number of row to be edited
        row_data: List of ints or floats of values to be edited in row
        row_columns: 
            List of column names ordered from left to right  
            - must be in the same order as in the table in the database
        table_name: name of table of row to be edited

    Raises:

    """
    db = Database()
    db.modify_row(table_name, row_num, row_data=row_data, row_columns=row_columns, mode="edit")


@router.patch("/add_point", status_code=200)
async def add_point(
        row_data: List[List[Any]],
        row_columns: List[str],
        table_name: str
):
    """
    Adds a point to a given table in the database.

    params: 
        row_data: 
            a List of all rows to be added  
            - Each List contains a List of either ints, floats, or times
        row_columns: 
            a List of all the columns in a table ordered from left to right  
            - must be in the same order as in the table in the database
        table_name: name of table of row to be added

    Raises:

    """
    db = Database()
    db._insert_rows(table_name, row_columns, row_data)

@router.patch("/remove_point", status_code=200)
async def remove_point(
        row_num: int,
        table_name: str
):
    """
    Removes a point from a given table in the database.

    params: 
        row_num: row number of row to be deleted
        table_name: name of table of row to be deleted

    Raises:

    """
    db = Database()
    db.modify_row(table_name, row_num,mode="delete")

@router.patch("/add_column", status_code=200)
async def add_column(
        column_name: List[str],
        column_type: List[str],
        table_name: str
):
    """
    Add one or more columns to an existing table.

    params:
        column_name: List of column names to add.
        column_type: Corresponding list of column data types.
        table_name: Name of the target table.
    """
    db = Database()
    db._add_column(table_name, column_name, column_type)

@router.patch("/delete_column", status_code=200)
async def delete_column(
        table_name: str,
        column_name: List[str],
):
    """
    Delete one or more columns from a table.

    params:
        table_name: Name of the target table.
        column_name: List of column names to remove.
    """
    db = Database()
    db._delete_column(table_name, column_name)

@router.patch("/rename_column", status_code=200)
async def rename_column(
        table_name: str,
        old_column_name: str,
        new_column_name: str
):
    """
    Rename a column in a table.

    params:
        table_name: Name of the target table.
        old_column_name: Current column name.
        new_column_name: Desired new column name.
    """
    db = Database()
    db.rename_column(table_name,old_column_name,new_column_name)

@router.post("/create_table", status_code=200)
async def create_table(
        table_name: str,
        column_name: List[str],
        column_type: List[str],
        project_id: int | None = None
):
    """
    Create a new database table for a project.

    params:
        table_name: Name of the table to create.
        column_name: List of column names.
        column_type: List of corresponding column types.
        project_id: Optional project ID to associate with the table.

    returns:
        (dict): table_name - A dictionary containing the created table name.
    """
    db = Database()
    db.create_table(table_name, column_name, column_type,project_id)
    db.update_last_updated(table_name)
    return {"table_name": table_name}

@router.post("/upload_manual", status_code=200)
async def upload_manual(
        json_in: str,
        project_id: int,
        table_name: str,
):
    """
    Uploads a series of manually entered data in a json string dict format to the Database

    params:
        json_in: json string with all data to be uploaded
        table_name: name of table to be uploaded

    Returns: 
        (str): 
            table_name - name of table created
        (str): 
            json - inputted json string

    Raises:

    """
    if project_id is None:
        project_id = 1
    db = Database()
    df = pd.DataFrame(json.loads(json_in))
    db.df_create_table(project_id, table_name, df)  # come back to for project_id
    db.update_last_updated(table_name)
    return {"table_name": table_name, "json": json_in}

@router.post("/upload_csv/")
async def upload_csv(
        project_id: int,
        table_name: str | None,
        file: UploadFile = File(...),
):
    """
    Upload a CSV file as a new table.

    params:
        table_name: Name of the table to be created[^1][^2]
        project_id: Project ID of project to add the table to.
        file: the file to be read and uploaded to the database. 

    [^1]: Cannot have same name as other table
    [^2]: Optional, if left blank tablename will take the csv filename

    Returns: 
        (str): table_name - name of file of created table
        (str): rows_count - number of rows

    Raises:

    """
    if project_id is None:
        project_id = 1
    db = Database()
    df = pd.read_csv(BytesIO(await file.read()))
    if table_name is None:
        table_name = file.filename
    db.df_create_table(project_id, table_name, df)  # come back to for project_id
    db.update_last_updated(table_name)
    return {"filename": file.filename, "rows_count": len(df)}

# originally generated with AI
@router.post("/upload_excel/", status_code=200)
async def upload_excel_file(
        project_id: int | None,
        file: UploadFile = File(...)
):
    """
    Receives an Excel file and processes it using pandas.

    params: 
        project_id: Project ID of project to add table to.
        file: the file to be read and uploaded to the database

    Returns: 
        (str): filename - .xlsx file prefix,
        (int): rows - num of rows,
        (int): columns - num of cols,
        (dict): data_sample - dataframe head - see pandas.dataframe.head

    Raises:

    """
    if project_id is None:
        project_id = 1
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
    db.df_create_table(project_id, file.filename.replace(".xlsx", ""), df)
    db.update_last_updated(file.filename.replace(".xlsx", ""))

    # Process the DataFrame (e.g., convert to JSON or perform analysis)
    # Returning a dictionary, which FastAPI serializes to JSON
    return {
        "filename": file.filename,
        "rows": len(df),
        "columns": len(df.columns),
        # You can return the data in JSON format for the client
        "data_sample": df.head().to_dict(orient="records")
    }

