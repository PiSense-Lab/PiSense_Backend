from pydantic import BaseModel
from typing import List, Dict, Any

class DataTable(BaseModel):
    data: List[Dict[str, Any]]
