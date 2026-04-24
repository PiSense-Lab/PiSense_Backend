import pandas as pd
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from io import BytesIO, StringIO
from pisense.backend.classes import Database

router = APIRouter(prefix="/output_format")


@router.get("/excel")
async def excel_output(
        project_id: int,
        tablename: str
):
    """
    Gets a table from a project and returns a xlsx file of that table.

    params:
        project_id: ID of the project the table is in
        tablename: name of the table to get

    Returns:
        (StreamingResponse): res - excel (xlsx) file itself with the tablename as the filename
    """
    db = Database()

    raw_df = db.get_table(table_name=tablename, project_id=project_id)

    bio = BytesIO()

    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        raw_df.to_excel(writer, index=False)

    bio.seek(0)

    res = StreamingResponse(
            bio,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f"attachment; filename={tablename}.xlsx"}
            )

    return res

@router.get("/csv")
async def csv_output(
        project_id: int,
        tablename: str
):
    """
    Gets a table from a project and returns a csv file of that table.

    params:
        project_id: ID of the project the table is in
        tablename: name of the table to get

    Returns:
        (StreamingResponse): res - csv file itself with the tablename as the filename
    """
    db = Database()

    raw_df = db.get_table(table_name=tablename, project_id=project_id)

    sio = StringIO()

    raw_df.to_csv(sio, index=False)

    sio.seek(0)
    output = sio.read()

    res = StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={tablename}.csv"}
            )

    return res
