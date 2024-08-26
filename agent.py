import json
from os import path
from openai import OpenAI
from message import Message, ALLOWED_MESSAGE_TYPES
from action import Action

class Agent:
    def __init__(self, alias, name, agent_type, identity, available_actions, military_power, economic_power, goal, description, client, use_full_identity, known_entities):
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
        self.known_entities = known_entities  # Dictionary mapping aliases to full names
        self.messages_config = self.load_messages_config()
        self.system_prompt = self.generate_system_prompt()

        
    def load_messages_config(self):
        script_dir = path.dirname(path.abspath(__file__))
        file_path = path.join(script_dir, "config/messages.json")
        with open(file_path) as f:
            return json.load(f)
    
    def generate_system_prompt(self):
        # Decide whether to use the full name or alias based on the use_full_identity flag
        name_or_alias = self.name if self.use_full_identity else self.alias

        # Prepare a detailed description of known entities with context
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


    async def act(self, context, personal_messages, public_statements):
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

    def validate_action(self, action):
        """
        Validates the action. If an action does not require a target,
        skip the object validation.
        """
        # Define actions that do not require a target
        actions_without_target = ["recruitment", "propaganda"]

        # If the action does not require a target, return early
        if action.action in actions_without_target:
            return

        # If the action requires a target, validate the target
        if action.object not in self.known_entities:
            raise ValueError(f"Invalid target entity '{action.object}' for action '{action.action}'.")

    async def decide_and_send_messages(self, world_state, personal_messages, public_statements, relations_matrix):
        # Determine agent's religion for alliance preference
        agent_religion = self.identity.split()[-1]  # Assuming the last word indicates the religion

        # Find potential allies of the same religion
        same_religion_allies = [
            alias for alias, details in self.known_entities.items()
            if details['identity'].split()[-1] == agent_religion and relations_matrix[self.alias][alias] == 0
        ]

        # Find potential allies (neutral relations)
        potential_allies = [
            alias for alias, relation in relations_matrix[self.alias].items() if relation == 0
        ]

        # Find enemies (negative relations)
        enemies = [
            alias for alias, relation in relations_matrix[self.alias].items() if relation == -1
        ]

        # Construct the user prompt
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

    def validate_message(self, message):
        if message.recipient not in self.known_entities and message.recipient != "PUBLIC":
            raise ValueError(f"Invalid recipient '{message.recipient}' for message. Please use only the known aliases.")
        if message.message_type not in ALLOWED_MESSAGE_TYPES.__args__:
            raise ValueError(f"Invalid message type '{message.message_type}'. Please use only the allowed message types.")

    

    def validate_message(self, message):
        if message.recipient not in self.known_entities and message.recipient != "PUBLIC":
            raise ValueError(f"Invalid recipient '{message.recipient}' for message. Please use only the known aliases.")
        if message.message_type not in ALLOWED_MESSAGE_TYPES.__args__:
            raise ValueError(f"Invalid message type '{message.message_type}'. Please use only the allowed message types.")

        if message.recipient not in self.known_entities and message.recipient != "PUBLIC":
            raise ValueError(f"Invalid recipient '{message.recipient}' for message. Please use only the known aliases.")

    
    
    def read_messages(self, mail):
        return mail.read(self.alias)

    def read_public_statements(self, mail):
        return mail.read_public_statements()
