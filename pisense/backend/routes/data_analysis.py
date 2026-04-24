from fastapi import APIRouter

router = APIRouter(prefix="/analysis")

#@router.get("/z_detect_anomalies")
#async def z_detect_outliers(
#        project_id: int,
#        tablename: str,
#):
#    db = Database()
#    undet = db.get_table(project_id=project_id)


#@router.get("/mad_detect_anomalies")
#async def mad_detect_outliers(
#        project_id: int,
#        tablename: str
#):

