from fastapi import APIRouter
from pisense.backend.classes import Database
import pandas as pd

router = APIRouter(prefix="/analysis")



@router.get("/z_detect_anomalies")
async def z_detect_outliers(
        project_id: int,
        tablename: str,
        y_title: str
):
    db = Database()

    raw = db.get_table(tablename, project_id=project_id)
    undet = pd.DataFrame(raw)
    z = (undet[y_title] - undet[y_title].expanding().mean()) / undet[y_title].expanding().std()
    print(z)
    return z

#@router.get("/mad_detect_anomalies")
#async def mad_detect_outliers(
#        project_id: int,
#        tablename: str
#):

