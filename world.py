# world.py
import json
from os import path
from update import UpdateItem, UpdateList
from action import Action  

class World:
    def __init__(self, agents, relations_matrix, mail, logger, client):
        self.agents = {agent.alias: agent for agent in agents}
        self.relations_matrix = relations_matrix
        self.mail = mail
        self.states = []
        self.actions_effects = self.load_action_effects()
        self.logger = logger
        self.client = client

    def load_action_effects(self):
        script_dir = path.dirname(path.abspath(__file__))
        file_path = path.join(script_dir, "config/action_effects.json")
        with open(file_path) as f:
            return json.load(f)

    def get_current_state(self):
        state = {
            "actions": {agent.alias: [] for agent in self.agents.values()},
            "military_strength": {agent.alias: agent.military_power for agent in self.agents.values()},
            "economic_strength": {agent.alias: agent.economic_power for agent in self.agents.values()},
            "relations_matrix": self.relations_matrix.relations
        }
        return state

    def add_action(self, agent_alias, action):
        current_state = self.states[-1] if self.states else self.get_current_state()
        current_state["actions"][agent_alias].append(action.model_dump())

    def record_state(self):
        state = self.get_current_state()
        self.states.append(state)
        if len(self.states) > 3:  # Keep only the latest 3 states
            self.states.pop(0)

    
    def calculate_action_outcomes(self, latest_actions):
        """
        Calculates the outcomes of the latest actions based on agents' military and economic power.
        """
        outcomes = []

        # Evaluate battles and their outcomes
        battles = {}
        for action in latest_actions:
            if action.action == "military attack":
                if action.object not in battles:
                    battles[action.object] = []
                battles[action.object].append(action)

        for defender, attackers in battles.items():
            defender_power = self.agents[defender].military_power
            total_attacker_power = sum(self.agents[attacker.subject].military_power for attacker in attackers)

            # Determine the outcome based on the strength comparison
            if total_attacker_power > defender_power:
                outcome = {
                    "defender": defender,
                    "attackers": [attacker.subject for attacker in attackers],
                    "result": "loss",
                    "military_change": defender_power - total_attacker_power,  # Decrease in military power
                    "economic_change": -abs(defender_power - total_attacker_power) // 2  # Economic impact of the loss
                }
            else:
                outcome = {
                    "defender": defender,
                    "attackers": [attacker.subject for attacker in attackers],
                    "result": "win",
                    "military_change": defender_power - total_attacker_power,  # Adjust based on defense
                    "economic_change": abs(defender_power - total_attacker_power) // 2  # Economic impact of the win
                }
            
            outcomes.append(outcome)

        return outcomes
    
   
    async def decide(self, latest_actions):
        serializable_actions = [action.model_dump() if isinstance(action, Action) else action for action in latest_actions]

        context = {
            "states": self.states,
            "latest_actions": serializable_actions,
            "action_effects": self.actions_effects
        }

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
            messages=[
                {"role": "system", "content": decision_prompt}
            ],
            response_format=UpdateList
        )

        # print(f"API Response: {response.choices[0].message.parsed}")

        updates_parsed = response.choices[0].message.parsed

        return self.parse_updates(updates_parsed)



    def parse_updates(self, updates_parsed: UpdateList):
        try:
            # Ensure updates_parsed is of the correct type
            if not isinstance(updates_parsed, UpdateList):
                raise TypeError("Parsed updates should be an UpdateList object.")
            
            return updates_parsed.updates
        except Exception as e:
            print(f"Error parsing updates: {e}")
            return []


    
    def apply_updates(self, updates):
        for update in updates:
            if not isinstance(update, UpdateItem):
                update = UpdateItem(**update)
            
            agent = self.agents.get(update.agent_name)
            if agent:
                # Calculate the absolute changes based on percentages
                military_change = agent.military_power * (update.military_change_percentage / 100.0)
                economic_change = agent.economic_power * (update.economic_change_percentage / 100.0)

                # Apply changes while ensuring non-negative values
                agent.military_power = max(0, agent.military_power + military_change)
                agent.economic_power = max(0, agent.economic_power + economic_change)

                
            else:
                raise ValueError(f"Invalid agent name in updates: {update.agent_name}")

    def process_messages(self):
        for agent in self.agents.values():
            messages = agent.read_messages(self.mail)
            for message in messages:
                # Process different types of messages and update relations accordingly
                if message.message_type == "Declare war":
                    self.relations_matrix.update_relations(message.sender, message.recipient, -1)

                elif message.message_type == "Propose alliance":
                    self.relations_matrix.update_relations(message.sender, message.recipient, 0)

                elif message.message_type == "Accept alliance":
                    self.relations_matrix.update_relations(message.sender, message.recipient, 1)

                elif message.message_type == "Reject alliance":
                    self.relations_matrix.update_relations(message.sender, message.recipient, -1)

                elif message.message_type == "Break alliance":
                    self.relations_matrix.update_relations(message.sender, message.recipient, -1)

                elif message.message_type == "Offer truce":
                    self.relations_matrix.update_relations(message.sender, message.recipient, 0)

                elif message.message_type == "Accept truce":
                    self.relations_matrix.update_relations(message.sender, message.recipient, 0)

                elif message.message_type == "Reject truce":
                    self.relations_matrix.update_relations(message.sender, message.recipient, -1)

                # Add other cases as needed

    def process_public_statements(self, public_statements):
        for statement in public_statements:
            if statement.message_type == "Declare war":
                self.relations_matrix.update_relations(statement.sender, statement.recipient, -1)
            elif statement.message_type == "Propose alliance":
                if self.relations_matrix.relations[statement.sender][statement.recipient] == 0:
                    self.relations_matrix.update_relations(statement.sender, statement.recipient, 1)
            elif statement.message_type == "Break alliance":
                self.relations_matrix.update_relations(statement.sender, statement.recipient, -1)
            elif statement.message_type == "Accept alliance":
                self.relations_matrix.update_relations(statement.sender, statement.recipient, 1)
            elif statement.message_type == "Reject alliance":
                self.relations_matrix.update_relations(statement.sender, statement.recipient, -1)
            elif statement.message_type == "Offer truce":
                self.relations_matrix.update_relations(statement.sender, statement.recipient, 0)
            elif statement.message_type == "Accept truce":
                self.relations_matrix.update_relations(statement.sender, statement.recipient, 0)
            elif statement.message_type == "Reject truce":
                self.relations_matrix.update_relations(statement.sender, statement.recipient, -1)
            # Add more public statement types and their effects on relations as needed

