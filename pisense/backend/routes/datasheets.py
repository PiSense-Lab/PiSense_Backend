from fastapi import APIRouter, File, UploadFile, status, HTTPException
from io import BytesIO
import pandas as pd
import json
from typing import Any, List
from pisense.backend.classes import USER_ROLES, Database
from pisense.backend.models.table_models import DataTable


router = APIRouter(prefix="/datatables")


# make it return the row numbers and the tablenames
#   of all the tables in a project
@router.get("/")
async def read_tables(project_id: int | None = None):
    """
    Return table metadata for all tables or for a specific project.

    params:
        project_id: Optional project ID to filter tables by project.

    returns:
        List of table metadata records.
    """
    db = Database()

    if project_id is None:
        res = db.get_table(project_id=None)  # or define a clearer "get_all"
    else:
        res = db.get_table(project_id=project_id)

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
        A DataTable response containing the requested rows.
    """
    db = Database()
    res = db._get_rows(table, columns, where_condition)

    return {"data": res}

@router.get("/get_users")
async def get_users(username: str | None = None):
    """
    Retrieve user records.

    params:
        username: Optional username to filter results.

    returns:
        List of user objects or matching user records.
    """
    db = Database()
    return db.get_users(username=username)

@router.get("/get_project")
async def get_project(project_id: int, name: str | None = None):
    """
    Retrieve a single project record.

    params:
        project_id: ID of the project to retrieve.
        name: Optional project name to filter by.

    returns:
        A project dictionary with id, name, description, public, archived, and owner_id.
    """
    db = Database()
    res = db.get_project(project_id, name=name)
    return {
        "id": res.id,
        "name": res.name,
        "description": res.description,
        "public": res.public,
        "archived": res.archived,
        "owner_id": res.owner_id,
    }

@router.get("/get_user_projects")
async def get_user_projects(user_id: int | None = None):
    """
    Retrieve projects associated with a user.

    params:
        user_id: Optional user ID to filter projects.

    returns:
        A dictionary containing project records for the user.
    """
    db = Database()
    res = db.get_projects_for_user(user_id)
    return {"data": res}

@router.post("/create_project", status_code=201)
async def create_project(
    name: str,
    owner_id: int,
    description: str = "",
    public: bool = False,
    archived: bool = False,
):
    """
    Create a new project.

    params:
        name: Name of the new project.
        owner_id: User ID that owns the project.
        description: Optional description of the project.
        public: Whether the project is public.
        archived: Whether the project is archived.

    returns:
        The created project record.
    """
    db = Database()
    project = db.create_project(
        name=name,
        owner_id=owner_id,
        description=description,
        public=public,
        archived=archived,
    )
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "public": project.public,
        "archived": project.archived,
        "owner_id": project.owner_id,
    }

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
        A dictionary containing the created table name.
    """
    db = Database()
    db.create_table(table_name, column_name, column_type,project_id)
    return {"table_name": table_name}

@router.post("/upload_manual", status_code=200)
async def upload_manual(
        json_in: str,
        table_name: str
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
    """
    Upload a CSV file as a new table.

    params:
        table_name: Optional target table name. If omitted, the CSV filename is used.
        project_id: Optional project ID to associate the table with.
        file: Uploaded CSV file.

    returns:
        The uploaded filename and number of rows imported.
    """
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

@router.get("/{table_name}", response_model=DataTable)
async def read_single_table(
    table_name: str,
    project_id: int | None = None
):
    """
    Retrieve a single table by name.

    params:
        table_name: Name of the table to retrieve.
        project_id: Optional project ID to filter by project association.

    returns:
        A DataTable response containing the table data.
    """
    db = Database()

    res = db.get_table(table_name=table_name, project_id=project_id)

    return {"data": res}
