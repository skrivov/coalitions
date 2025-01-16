"""
agent.py

Defines an Agent class that encapsulates an AI-driven or rule-based character
with its own state, identity, and decision-making processes.
"""

from __future__ import annotations
import json
from os import path
from typing import Any
from message import Message, ALLOWED_MESSAGE_TYPES
from action import Action
from mail import Mail


class Agent:
    """
    Represents an individual agent (e.g., a country or entity) with objectives, power metrics,
    and the ability to read messages, decide actions, and respond.
    """

    def __init__(
        self,
        alias: str,
        name: str,
        agent_type: str,
        identity: str,
        available_actions: list[str],
        military_power: float,
        economic_power: float,
        goal: str,
        description: str,
        client: Any,
        use_full_identity: bool,
        known_entities: dict[str, dict[str, str]]
    ) -> None:
        """
        Initializes an Agent with given attributes.

        Args:
            alias (str): The short alias for the agent (e.g., "A1").
            name (str): The full descriptive name of the agent.
            agent_type (str): The type of the agent (e.g., "country").
            identity (str): A string describing the agent's identity or role.
            available_actions (list[str]): The list of possible actions this agent can perform.
            military_power (float): The military power level of the agent.
            economic_power (float): The economic power level of the agent.
            goal (str): The primary goal or objective of this agent.
            description (str): A textual description of the agent.
            client (Any): An asynchronous AI client for generating behavior.
            use_full_identity (bool): Whether to refer to entities by full name or alias.
            known_entities (dict[str, dict[str, str]]): A dictionary mapping from alias to entity details (name, identity).
        """
        self.alias = alias
        self.name = name
        self.type = agent_type
        self.identity = identity
        self.available_actions = available_actions
        self.military_power = military_power
        self.economic_power = economic_power
        self.goal = goal
        self.description = description
        self.client = client
        self.use_full_identity = use_full_identity
        self.known_entities = known_entities
        self.messages_config: dict[str, Any] = self.load_messages_config()
        self.system_prompt: str = self.generate_system_prompt()

    def load_messages_config(self) -> dict[str, Any]:
        """
        Loads the messages configuration file to guide agent responses.

        Returns:
            dict[str, Any]: A dictionary representing the loaded JSON configuration.
        """
        script_dir = path.dirname(path.abspath(__file__))
        file_path = path.join(script_dir, "config/messages.json")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def generate_system_prompt(self) -> str:
        """
        Generates a system prompt string incorporating agent details, known entities, and instructions.

        Returns:
            str: The generated system prompt for conversation with an AI model.
        """
        name_or_alias = self.name if self.use_full_identity else self.alias

        if self.use_full_identity:
            known_entities_str = '\n'.join([
                f"- Alias: {alias} | Full Name: {details['name']} | Description: {details['identity']}"
                for alias, details in self.known_entities.items()
            ])
        else:
            known_entities_str = '\n'.join([
                f"- Alias: {alias} | Description: {details['identity']}"
                for alias, details in self.known_entities.items()
            ])

        return f"""
        You are {name_or_alias}, a {self.type}. You are {self.identity}
        
        Your primary objective is:
        - {self.goal}
        
        You must always act according to your identity and objectives in all interactions.

        Context of Known Entities and Their Aliases:
        {known_entities_str}
        
        Important Instructions:
        - Refer to all entities by their alias in all communications and actions.
        - Ensure any actions or messages are directed to one of the known entities.
        - For actions such as defense or military attack, always specify a valid target entity.
        
        Based on this, determine your next action and send necessary messages.
        """

    async def act(
        self,
        context: str,
        personal_messages: str,
        public_statements: str
    ) -> Action:
        """
        Determines and returns the next action for the agent using an AI model.

        Args:
            context (str): A JSON-serialized representation of the current world state.
            personal_messages (str): JSON string of personal messages for the agent.
            public_statements (str): JSON string of public statements relevant to the agent.

        Returns:
            Action: The next action chosen by the agent.
        """
        user_prompt = f"""
        Your military power is {self.military_power} and your economic power is {self.economic_power}.
        Your current goal is: {self.goal}.
        
        Consider the following information:
        - Personal Messages: {personal_messages}
        - Public Statements: {public_statements}

        {context}
        Choose your next action from the following options:
        {', '.join(self.available_actions + ["NONE"])}
        
        Remember:
        - You must use only the aliases of known entities for any actions or messages.
        
        Provide the action output in the following JSON format:
        {{
            "subject": "{self.alias}",
            "object": "<Target Agent or None>",
            "action": "<Action>"
        }}
        """
        response = await self.client.beta.chat.completions.parse(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=Action
        )
        action = response.choices[0].message.parsed
        self.validate_action(action)
        return action

    def validate_action(self, action: Action) -> None:
        """
        Validates whether the action requires a target and checks if it is recognized.
        """
        # Define actions that do NOT require a target
        actions_without_target = ["NONE", "recruitment", "propaganda"]

        # If the action is one of the above, skip the target validation
        if action.action in actions_without_target:
            return

        # Otherwise, if it DOES require a target, check if that target is known
        if action.object not in self.known_entities:
            raise ValueError(
                f"Invalid target entity '{action.object}' for action '{action.action}'."
            )


    async def decide_and_send_messages(
        self,
        world_state: str,
        personal_messages: str,
        public_statements: str,
        relations_matrix: dict[str, dict[str, int]]
    ) -> list[Message]:
        """
        Decides whether to send any messages to other agents based on the agent's goals, religion, or known data.

        Args:
            world_state (str): A JSON-serialized representation of the current world state.
            personal_messages (str): JSON string of personal messages for the agent.
            public_statements (str): JSON string of public statements relevant to the agent.
            relations_matrix (dict[str, dict[str, int]]): Current relations matrix between agents.

        Returns:
            list[Message]: A list of messages to be sent (could be empty).
        """
        agent_religion = self.identity.split()[-1]
        same_religion_allies = [
            alias for alias, details in self.known_entities.items()
            if details['identity'].split()[-1] == agent_religion and relations_matrix[self.alias][alias] == 0
        ]
        potential_allies = [
            alias for alias, relation in relations_matrix[self.alias].items() if relation == 0
        ]
        enemies = [
            alias for alias, relation in relations_matrix[self.alias].items() if relation == -1
        ]

        user_prompt = f"""
        Based on the current world state and the following information:
        - Personal Messages: {personal_messages}
        - Public Statements: {public_statements}
        - Relations Matrix: {relations_matrix}
        
        Decide if you need to send any messages to other agents to achieve your goal.
        
        Consider the following preferences and constraints:
        - Agents of the same religion are preferred for alliances.        
        - Avoid proposing alliances to agents you are already allied with or who are enemies (-1).
        - You can declare war on any agent with whom you have negative (-1) relations.
        - Specify a valid message type from the following options:
        ["Propose alliance", "Accept alliance", "Reject alliance", "Break alliance",
        "Declare war", "Offer truce", "Accept truce", "Reject truce",
        "Public statement", "NONE"]

        Potential Allies (same religion): {same_religion_allies}
        Potential Allies (neutral relations): {potential_allies}
        Enemies (negative relations): {enemies}

        Provide the messages output in the following JSON format:
        {{
            "from": "{self.alias}",
            "to": "<Recipient Agent or PUBLIC>",
            "content": "<Message Content>",
            "message_type": "<Message Type>"
        }}
        """
        response = await self.client.beta.chat.completions.parse(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=Message
        )

        message = response.choices[0].message.parsed
        self.validate_message(message)
        return [message]

    def validate_message(self, message: Message) -> None:
        """
        Validates whether the message is addressed to a known entity or 'PUBLIC' and that the message type is valid.

        Args:
            message (Message): The message to validate.

        Raises:
            ValueError: If the recipient or message type is invalid.
        """
        if message.recipient not in self.known_entities and message.recipient != "PUBLIC":
            raise ValueError(
                f"Invalid recipient '{message.recipient}' for message. Please use only the known aliases."
            )

        if message.message_type not in ALLOWED_MESSAGE_TYPES.__args__:
            raise ValueError(
                f"Invalid message type '{message.message_type}'. Please use only the allowed message types."
            )

    def read_messages(self, mail: Mail) -> list[Message]:
        """
        Reads private messages from the mail system for this agent.

        Args:
            mail (Mail): The mail system to read from.

        Returns:
            list[Message]: A list of messages addressed to this agent.
        """
        return mail.read(self.alias)

    def read_public_statements(self, mail: Mail) -> list[Message]:
        """
        Reads public statements from the mail system.

        Args:
            mail (Mail): The mail system to read from.

        Returns:
            list[Message]: A list of public messages.
        """
        return mail.read_public_statements()
