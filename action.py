"""
action.py

Defines an Action model for agent actions.
"""

from __future__ import annotations
from pydantic import BaseModel


class Action(BaseModel):
    """
    A model representing an action taken by an agent.
    """
    subject: str
    object: str | None
    action: str

    def to_json(self) -> str:
        """
        Serializes the action to a JSON string.

        Returns:
            str: The JSON representation of the action.
        """
        return self.model_dump_json()

    @classmethod
    def from_json(cls, json_str: str) -> Action:
        """
        Deserializes a JSON string to an Action object.

        Args:
            json_str (str): The JSON representation of an action.

        Returns:
            Action: The instantiated action object.
        """
        return cls.model_validate_json(json_str)
