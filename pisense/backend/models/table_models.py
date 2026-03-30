from pydantic import BaseModel, RootModel, ConfigDict
from typing import List
from datetime import time

class DataPoint(BaseModel):
    DateTime: time
    Value: float | int | None

class DataRow(BaseModel):
    DateTime: time
    Value: float | int | None
    model_config = ConfigDict(
            extra='allow'
            )

class DataTable(BaseModel):
    data: List[DataRow]

class DataTables(RootModel):
    root: List[DataTable]

