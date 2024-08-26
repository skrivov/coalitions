from pydantic import BaseModel, Field
from typing import Literal

# Define allowed message types based on your JSON spec
ALLOWED_MESSAGE_TYPES = Literal[
    "Propose alliance", "Accept alliance", "Reject alliance", "Break alliance",
    "Declare war", "Offer truce", "Accept truce", "Reject truce",
    "Public statement", "NONE"
]

class Message(BaseModel):
    sender: str
    recipient: str
    content: str
    message_type: ALLOWED_MESSAGE_TYPES  # New field for message type

    def to_json(self):
        return self.model_dump_json()
    
    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_json(cls, json_str):
        return cls.model_validate_json(json_str)
