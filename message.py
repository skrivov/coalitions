"""
message.py

Defines the Message model and allowed message types for agent communication.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal


# Define allowed message types based on your JSON spec
ALLOWED_MESSAGE_TYPES = Literal[
    "Propose alliance",
    "Accept alliance",
    "Reject alliance",
    "Break alliance",
    "Declare war",
    "Offer truce",
    "Accept truce",
    "Reject truce",
    "Public statement",
    "NONE"
]


class Message(BaseModel):
    """
    A model representing a message object exchanged between agents.
    """
    sender: str
    recipient: str
    content: str
    message_type: ALLOWED_MESSAGE_TYPES

    def to_json(self) -> str:
        """
        Serializes the Message to JSON format.

        Returns:
            str: The JSON representation of the message.
        """
        return self.model_dump_json()

    def to_dict(self) -> dict[str, str]:
        """
        Converts the Message to a dictionary.

        Returns:
            dict[str, str]: The dictionary representation of the message.
        """
        return self.model_dump()

    @classmethod
    def from_json(cls, json_str: str) -> Message:
        """
        Deserializes a JSON string to a Message object.

        Args:
            json_str (str): The JSON representation of a message.

        Returns:
            Message: The instantiated message.
        """
        return cls.model_validate_json(json_str)
