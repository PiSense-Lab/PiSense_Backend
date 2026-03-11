from pydantic import BaseModel
from typing import List, Union
from datetime import datetime


class DataTable(BaseModel):
    time: List[str]
    user_id: int
    value: List[Union[float | int]]
    e_val1: List[Union[float | int | None]]
    e_val2: List[Union[float | int | None]]
    e_val3: List[Union[float | int | None]]
    e_val4: List[Union[float | int | None]]
    e_val5: List[Union[float | int | None]]


class DataPoint(BaseModel):
    time: str
    user_id: int
    value: float | int | None
