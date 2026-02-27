from pydantic import BaseModel, Union
from datetime import datetime


class DataTable(BaseModel):
    time: datetime
    user_id: int
    value: Union(float, int)
    e_val1: Union(float, int)
    e_val2: Union(float, int)
    e_val3: Union(float, int)
    e_val4: Union(float, int)
    e_val5: Union(float, int)
