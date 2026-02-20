from pydantic import BaseModel
from datetime import datetime


class HourlyRecord(BaseModel):
    date: datetime
    temperature_2m: float


class DailyRecord(BaseModel):
    date: datetime
    temperature_2m_max: float
    temperature_2m_min: float
