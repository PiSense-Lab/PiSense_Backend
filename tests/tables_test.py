from fastapi import APIRouter, Depends
from pisense.backend.classes import Database
from pisense.backend.models.table_models import DataTable

router = APIRouter(prefix="/testing")


#for testing purposes 
@router.post("/upload")
async def test_upload(
        user_id: int | None,
        tablename: str
):
    db = Depends(Database())
    df = pd.read_csv("./ExampleData.csv")
    db.df_create_table(tablename, df, user_id)

    return f"Table created with user: {user_id} and tablename: {tablename}"
