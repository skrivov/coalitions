"""
world.py

Defines the World class which manages agent interactions, states, actions, and relation updates.
"""

from __future__ import annotations

import json
from os import path
from typing import Any
from update import UpdateItem, UpdateList
from action import Action
from mail import Mail
from agent import Agent
from relations_matrix import RelationsMatrix
import custom_logger as logger_module
from message import Message  


class World:
    """
    The World class encapsulates all agents, their relationships, mail communication, and state changes.
    """

    def __init__(
        self,
        agents: list[Agent],
        relations_matrix: RelationsMatrix,
        mail: Mail,
        logger: logger_module,
        client: Any
    ) -> None:
        """
        Initializes the world with agents, a relations matrix, mail system, logger, and an OpenAI client.

        Args:
            agents: A list of agent objects.
            relations_matrix: An object managing relationships between agents.
            mail: The mail system for messages.
            logger: A custom logger module for logging.
            client: An asynchronous OpenAI client or equivalent for generating decisions.
        """
        self.agents: dict[str, Agent] = {agent.alias: agent for agent in agents}
        self.relations_matrix = relations_matrix
        self.mail = mail
        self.states: list[dict[str, Any]] = []
        self.actions_effects: dict[str, Any] = self.load_action_effects()
        self.logger = logger
        self.client = client

    def load_action_effects(self) -> dict[str, Any]:
        """
        Loads action effects from a JSON configuration file.

        Returns:
            A dictionary containing action effect mappings.
        """
        script_dir = path.dirname(path.abspath(__file__))
        file_path = path.join(script_dir, "config/action_effects.json")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_current_state(self) -> dict[str, Any]:
        """
        Constructs and returns the current state of the world.

        Returns:
            A dictionary of the current world state, including actions, 
            military/economic strength, and relations.
        """
        state = {
            "actions": {agent.alias: [] for agent in self.agents.values()},
            "military_strength": {
                agent.alias: agent.military_power for agent in self.agents.values()
            },
            "economic_strength": {
                agent.alias: agent.economic_power for agent in self.agents.values()
            },
            "relations_matrix": self.relations_matrix.relations
        }
        return state

    def add_action(self, agent_alias: str, action: Action) -> None:
        """
        Adds an action to the latest recorded state or a new state if none is recorded yet.

        Args:
            agent_alias: The alias of the agent performing the action.
            action: The action taken by the agent.
        """
        current_state = self.states[-1] if self.states else self.get_current_state()
        current_state["actions"][agent_alias].append(action.model_dump())

    def record_state(self) -> None:
        """
        Records the current state of the world in the states list.
        Keeps only the latest 3 states to prevent unbounded growth.
        """
        state = self.get_current_state()
        self.states.append(state)
        if len(self.states) > 3:
            self.states.pop(0)

    def calculate_action_outcomes(self, latest_actions: list[Action]) -> list[dict[str, Any]]:
        """
        Calculates the outcomes of the latest actions (e.g., battles) based on agents' military power.

        Args:
            latest_actions: The list of actions taken by agents.

        Returns:
            A list of outcome dictionaries for each conflict or result.
        """
        outcomes: list[dict[str, Any]] = []
        battles: dict[str, list[Action]] = {}

        # Group attacks by their defender
        for action in latest_actions:
            if action.action == "military attack":
                battles.setdefault(action.object, []).append(action)

        # Evaluate battles and their outcomes
        for defender, attackers in battles.items():
            defender_power = self.agents[defender].military_power
            total_attacker_power = sum(
                self.agents[attacker.subject].military_power for attacker in attackers
            )

            if total_attacker_power > defender_power:
                outcome = {
                    "defender": defender,
                    "attackers": [attacker.subject for attacker in attackers],
                    "result": "loss",
                    "military_change": defender_power - total_attacker_power,
                    "economic_change": -abs(defender_power - total_attacker_power) // 2
                }
            else:
                outcome = {
                    "defender": defender,
                    "attackers": [attacker.subject for attacker in attackers],
                    "result": "win",
                    "military_change": defender_power - total_attacker_power,
                    "economic_change": abs(defender_power - total_attacker_power) // 2
                }
            outcomes.append(outcome)

        return outcomes

    async def decide(self, latest_actions: list[Action]) -> list[UpdateItem]:
        """
        Uses an AI model or client to determine how military and economic power 
        should be updated based on the latest actions.

        Args:
            latest_actions: The latest actions performed by agents.

        Returns:
            A list of update items detailing power percentage changes for each agent.
        """
        serializable_actions = [
            action.model_dump() if isinstance(action, Action) else action
            for action in latest_actions
        ]

        context = {
            "states": self.states,
            "latest_actions": serializable_actions,
            "action_effects": self.actions_effects
        }

        # Calculate known outcomes (e.g., battles)
        action_outcomes = self.calculate_action_outcomes(latest_actions)

        decision_prompt = f"""
        Based on the current and past states of the world and the latest actions by the agents:
        {json.dumps(context)}

        **Important Guidelines**:
        - Calculate changes in military and economic power as a percentage of the current values.
        - The percentage change should be within -10% to +10%.
        - Military power and economic power must not be negative. If an agent's power is reduced below zero, adjust it to zero.
        - Use a scaling factor based on the difference in strength between agents to determine the magnitude of changes.

        Determine how the military power and economic power should be updated for each agent.
        Provide the updates in the following JSON format:
        {{
            "updates": [
                {{
                    "agent_name": "<Agent Name>",
                    "military_change_percentage": <Percentage Change in Military Power>,
                    "economic_change_percentage": <Percentage Change in Economic Power>
                }},
                ...
            ]
        }}
        """

        response = await self.client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "system", "content": decision_prompt}],
            response_format=UpdateList
        )

        updates_parsed = response.choices[0].message.parsed
        return self.parse_updates(updates_parsed)

    def parse_updates(self, updates_parsed: UpdateList) -> list[UpdateItem]:
        """
        Parses the updates from an UpdateList and returns the contained UpdateItem list.

        Args:
            updates_parsed: A parsed UpdateList object from the AI response.

        Returns:
            A list of update items describing military/economic changes.
        """
        try:
            if not isinstance(updates_parsed, UpdateList):
                raise TypeError("Parsed updates should be an UpdateList object.")
            return updates_parsed.updates
        except Exception as e:
            print(f"Error parsing updates: {e}")
            return []

    def apply_updates(self, updates: list[UpdateItem]) -> None:
        """
        Applies the computed updates to each agent, ensuring that power values do not go negative.

        Args:
            updates: A list of update items describing percentage changes to agent power.
        """
        for update in updates:
            if not isinstance(update, UpdateItem):
                update = UpdateItem(**update)

            agent = self.agents.get(update.agent_name)
            if agent:
                military_change = agent.military_power * (update.military_change_percentage / 100.0)
                economic_change = agent.economic_power * (update.economic_change_percentage / 100.0)
                agent.military_power = max(0, agent.military_power + military_change)
                agent.economic_power = max(0, agent.economic_power + economic_change)
            else:
                raise ValueError(f"Invalid agent name in updates: {update.agent_name}")

    def process_messages(self) -> None:
        """
        Instructs each agent to read their private messages and processes
        the message types (e.g., war declarations, alliance proposals).
        """
        for agent in self.agents.values():
            messages = agent.read_messages(self.mail)
            for message in messages:
                if message.message_type == "Declare war":
                    self.relations_matrix.update_relations(
                        message.sender, message.recipient, -1
                    )
                elif message.message_type == "Propose alliance":
                    self.relations_matrix.update_relations(
                        message.sender, message.recipient, 0
                    )
                elif message.message_type == "Accept alliance":
                    self.relations_matrix.update_relations(
                        message.sender, message.recipient, 1
                    )
                elif message.message_type == "Reject alliance":
                    self.relations_matrix.update_relations(
                        message.sender, message.recipient, -1
                    )
                elif message.message_type == "Break alliance":
                    self.relations_matrix.update_relations(
                        message.sender, message.recipient, -1
                    )
                elif message.message_type == "Offer truce":
                    self.relations_matrix.update_relations(
                        message.sender, message.recipient, 0
                    )
                elif message.message_type == "Accept truce":
                    self.relations_matrix.update_relations(
                        message.sender, message.recipient, 0
                    )
                elif message.message_type == "Reject truce":
                    self.relations_matrix.update_relations(
                        message.sender, message.recipient, -1
                    )

    def process_public_statements(self, public_statements: list[Message]) -> None:
        """
        Processes public statements, updating the relations matrix accordingly.

        Args:
            public_statements: A list of publicly broadcast messages.
        """
        for statement in public_statements:
            if statement.message_type == "Declare war":
                self.relations_matrix.update_relations(
                    statement.sender, statement.recipient, -1
                )
            elif statement.message_type == "Propose alliance":
                if self.relations_matrix.relations[statement.sender][statement.recipient] == 0:
                    self.relations_matrix.update_relations(
                        statement.sender, statement.recipient, 1
                    )
            elif statement.message_type == "Break alliance":
                self.relations_matrix.update_relations(
                    statement.sender, statement.recipient, -1
                )
            elif statement.message_type == "Accept alliance":
                self.relations_matrix.update_relations(
                    statement.sender, statement.recipient, 1
                )
            elif statement.message_type == "Reject alliance":
                self.relations_matrix.update_relations(
                    statement.sender, statement.recipient, -1
                )
            elif statement.message_type == "Offer truce":
                self.relations_matrix.update_relations(
                    statement.sender, statement.recipient, 0
                )
            elif statement.message_type == "Accept truce":
                self.relations_matrix.update_relations(
                    statement.sender, statement.recipient, 0
                )
            elif statement.message_type == "Reject truce":
                self.relations_matrix.update_relations(
                    statement.sender, statement.recipient, -1
                )
