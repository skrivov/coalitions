"""
update.py

Defines classes for specifying updates to agents' military and economic power.
"""

from __future__ import annotations
from pydantic import BaseModel


class UpdateItem(BaseModel):
    """
    Represents a single update to an agent's power levels.
    """
    agent_name: str
    military_change_percentage: float
    economic_change_percentage: float


class UpdateList(BaseModel):
    """
    Represents a batch of updates to multiple agents.
    """
    updates: list[UpdateItem]

    def to_dict(self) -> dict[str, list[dict[str, float | str]]]:
        """
        Converts the update list to a dictionary.

        Returns:
            dict[str, list[dict[str, float | str]]]: Dictionary representation of the update list.
        """
        return self.model_dump()
