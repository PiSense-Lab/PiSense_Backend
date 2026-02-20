from pydantic import BaseModel
from datetime import datetime


class HourlyRecord(BaseModel):
    date: datetime
    temperature_2m: float
