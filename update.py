
from pydantic import BaseModel
from typing import List, Dict, Optional

class UpdateItem(BaseModel):
    agent_name: str
    military_change_percentage: float  # Changed from int to float for percentage change
    economic_change_percentage: float  # Changed from int to float for percentage change
    

class UpdateList(BaseModel):
    updates: List[UpdateItem]

    def to_dict(self):
        return self.model_dump()