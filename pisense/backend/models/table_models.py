from pydantic import BaseModel, RootModel, ConfigDict
from typing import List, Dict, Any
from pydantic import BaseModel

class DataTable(BaseModel):
    data: List[Dict[str, Any]]