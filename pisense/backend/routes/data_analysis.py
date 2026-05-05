from fastapi import APIRouter
from pisense.backend.classes import Database
import pandas as pd
import numpy as np

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
    z[np.isnan(z.astype(float))] = 0

    res_dict = {}
    for u_val, z_score, i in zip(undet[y_title], z, undet["index"]):
        if z_score >= 2 or z_score <= -2:
            res_dict[f"{i}"] = u_val
    return {"count": len(res_dict), "data": res_dict}

#@router.get("/mad_detect_anomalies")
#async def mad_detect_outliers(
#        project_id: int,
#        tablename: str
#):

