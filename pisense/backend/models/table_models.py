from pydantic import BaseModel
from datetime import datetime


class DataTable(BaseModel):
    time: datetime
    user_id: int
    value: float | int
    e_val1: float | int
    e_val2: float | int
    e_val3: float | int
    e_val4: float | int
    e_val5: float | int
