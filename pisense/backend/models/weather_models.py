from pydantic import BaseModel
from datetime import date, time


class HourlyRecord(BaseModel):
    # ISO timestamp
    date: date
    time: time
    temperature_2m: float


class DailyRecord(BaseModel):
    date: date
    time: time
    temperature_2m_max: float
    temperature_2m_min: float
