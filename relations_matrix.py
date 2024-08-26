import json

class RelationsMatrix:
    def __init__(self, config_path):
        self.relations = self.load_relations(config_path)

    def load_relations(self, config_path):
        with open(config_path) as f:
            relations_data = json.load(f)["relations"]
            relations_matrix = {alias: data["relations"] for alias, data in relations_data.items()}
            return relations_matrix

    def update_relations(self, agent1, agent2, val):        
        self.relations[agent1][agent2] = val
        self.relations[agent2][agent1] = val
        

    def get_friends(self, agent_name):
        return [alias for alias, relation in self.relations[agent_name].items() if relation > 0]

    def get_enemies(self, agent_name):
        return [alias for alias, relation in self.relations[agent_name].items() if relation < 0]

    def to_matrix(self, agent_aliases):
        matrix = [[self.relations[agent][other] for other in agent_aliases] for agent in agent_aliases]
        return matrix

    def to_user_friendly_format(self, agent_aliases):
        headers = [""] + agent_aliases
        table = [[agent] + [self.relations[agent][other] for other in agent_aliases] for agent in agent_aliases]
        return headers, table
