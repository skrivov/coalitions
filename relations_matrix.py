"""
relations_matrix.py

Defines a RelationsMatrix class to manage and update relationship values between agents.
"""

from __future__ import annotations
import json
from typing import Any 


class RelationsMatrix:
    """
    Manages the relationship values between agents, e.g., alliances, enmities, etc.
    """

    def __init__(self, config_path: str) -> None:
        """
        Initializes the relations matrix by loading data from a JSON configuration.

        Args:
            config_path (str): Path to the JSON file containing relations data.
        """
        self.relations: dict[str, dict[str, int]] = self.load_relations(config_path)

    def load_relations(self, config_path: str) -> dict[str, dict[str, int]]:
        """
        Loads the relations data from a JSON file.

        Args:
            config_path (str): Path to the JSON file.

        Returns:
            dict[str, dict[str, int]]: A mapping of agent alias to a dictionary of (other_alias -> relationship value).
        """
        with open(config_path, "r", encoding="utf-8") as f:
            relations_data: dict[str, Any] = json.load(f)["relations"]
            relations_matrix: dict[str, dict[str, int]] = {
                alias: data["relations"] for alias, data in relations_data.items()
            }
            return relations_matrix

    def update_relations(self, agent1: str, agent2: str, val: int) -> None:
        """
        Updates the relation value between two agents (and ensures it's mirrored).

        Args:
            agent1 (str): The first agent's alias.
            agent2 (str): The second agent's alias.
            val (int): The new relationship value.
        """
        self.relations[agent1][agent2] = val
        self.relations[agent2][agent1] = val

    def get_friends(self, agent_name: str) -> list[str]:
        """
        Returns a list of agents with positive relationships to the specified agent.

        Args:
            agent_name (str): The alias of the agent to retrieve friends for.

        Returns:
            list[str]: A list of agent aliases that have a positive relationship value.
        """
        return [alias for alias, relation in self.relations[agent_name].items() if relation > 0]

    def get_enemies(self, agent_name: str) -> list[str]:
        """
        Returns a list of agents with negative relationships to the specified agent.

        Args:
            agent_name (str): The alias of the agent to retrieve enemies for.

        Returns:
            list[str]: A list of agent aliases that have a negative relationship value.
        """
        return [alias for alias, relation in self.relations[agent_name].items() if relation < 0]

    def to_matrix(self, agent_aliases: list[str]) -> list[list[int]]:
        """
        Converts the internal relations dictionary to a matrix format.

        Args:
            agent_aliases (list[str]): A list of agent aliases in the desired matrix order.

        Returns:
            list[list[int]]: A 2D list representing the relations matrix.
        """
        return [
            [self.relations[agent][other] for other in agent_aliases]
            for agent in agent_aliases
        ]

    def to_user_friendly_format(self, agent_aliases: list[str]) -> tuple[list[str], list[list[Any]]]:
        """
        Prepares a user-friendly representation of the relations matrix for logging or display.

        Args:
            agent_aliases (list[str]): A list of agent aliases in the desired matrix order.

        Returns:
            tuple[list[str], list[list[Any]]]: Headers and table rows representing relationships.
        """
        headers = [""] + agent_aliases
        table = [
            [agent] + [self.relations[agent][other] for other in agent_aliases]
            for agent in agent_aliases
        ]
        return headers, table
