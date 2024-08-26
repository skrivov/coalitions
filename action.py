from pydantic import BaseModel

from pydantic import BaseModel
from typing import Optional

class Action(BaseModel):
    subject: str
    object: Optional[str]
    action: str

    def to_json(self):
        return self.model_dump_json()

    @classmethod
    def from_json(cls, json_str):
        return cls.model_validate_json(json_str)

    