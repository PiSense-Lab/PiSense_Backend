from fastapi import APIRouter, Depends, File, UploadFile, status
from io import BytesIO
from typing import Annotated
from pisense.backend.classes import Database
from pisense.backend.models.table_models import DataTable


router = APIRouter(prefix="/datatables")

@router.get("", response_model=list[DataTable])
async def read_tables(
        user_id: int | None = None
):
    db =  Depends(Database())
    if user_id is None:
        res = db.get_table()
    else:
        res = db.get_table(user_id=user_id)

    return res

@router.get("/{tablename}", response_model=DataTable)
async def read_single_table(
        tablename: str,
        user_id: int
):
    db =  Depends(Database())
    res = db.get_table(tablename, user_id)

    return res


@router.post("/upload-csv/")
async def upload_csv(
        tablename: str | None,
        user_id: int,
        file: UploadFile = File(...),
):
    db = Depends(Database())
    df = pd.read_csv(BytesIO(await file.read()))
    if tablename is None:
        tablename = file.filename
    db.df_create_table(tablename, df, user_id)
    return {"filename": file.filename, "rows_count": len(df)}


@router.post("/read_excel/", status_code=201)
async def upload_excel_file(
        user_id: int,
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
    
    db = Depends(Database())

    for key, value in df:
        db.df_create_table(key, value, user_id)

    # Process the DataFrame (e.g., convert to JSON or perform analysis)
    # Returning a dictionary, which FastAPI serializes to JSON
    return {
        "filename": file.filename,
        "rows": len(df),
        "columns": len(df.columns),
        # You can return the data in JSON format for the client
        "data_sample": df.head().to_dict(orient="records") 
    }

