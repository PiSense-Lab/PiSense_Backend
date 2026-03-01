from pydantic import BaseModel

class DataTable(BaseModel):
    time: str
    user_id: int
    value: float | int
    e_val1: float | int | None
    e_val2: float | int | None
    e_val3: float | int | None
    e_val4: float | int | None
    e_val5: float | int | None
