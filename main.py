import asyncio
import logging
import os
from os import path
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agent import Agent
from mail import Mail
from world import World
from relations_matrix import RelationsMatrix
from analytics import Analytics, measure_mse, measure_cosine_similarity, measure_jaccard_similarity, measure_pearson_correlation
import custom_logger as logger_module

async def simulation_loop(agents, world, rounds, analytics):
    logger_module.log_agents_intro(agents)
    logger_module.log_relations(world.relations_matrix.relations, agents)

    for step in range(rounds):
        # Record the state of the world
        world.record_state()

        # Step 1: Agents read existing public statements and private messages
        public_statements = world.mail.read_public_statements()
        message_tasks = [
            agent.decide_and_send_messages(
                json.dumps(world.get_current_state()),
                json.dumps([message.to_dict() for message in agent.read_messages(world.mail)]),  # Properly serialized messages
                json.dumps([statement.to_dict() for statement in public_statements]),  # Properly serialized public statements
                world.relations_matrix.relations  # Pass the relations matrix here
            ) for agent in agents
        ]
        messages_list = await asyncio.gather(*message_tasks)
       
        for agent, messages in zip(agents, messages_list):
            for message in messages:
                world.mail.send(message)
        logger_module.log_messages([msg for messages in messages_list for msg in messages])

        # Step 2: Agents take actions based on the state of the world, private messages, and public statements
        action_tasks = [
            agent.act(  # Ensure act() is awaited
                json.dumps(world.get_current_state()),
                json.dumps([message.to_dict() for message in agent.read_messages(world.mail)]),
                json.dumps([statement.to_dict() for statement in public_statements])
            ) for agent in agents
        ]
         

        latest_actions = await asyncio.gather(*action_tasks)
        for agent, action in zip(agents, latest_actions):
            world.add_action(agent.alias, action)
        logger_module.log_actions(latest_actions)

          # Step 3: Finalize messages and public statements
        world.mail.finalize()


        # Step 4: Process messages and public statements
        world.process_messages()
        world.process_public_statements(public_statements)

      

        # Step 5: Update world state based on interactions
        updates = await world.decide(latest_actions)
        world.apply_updates(updates)
        logger_module.log_agent_state(agents)

        # Step 6: Compute and log similarity to end state
        current_matrix = world.relations_matrix.to_matrix(world.relations_matrix.relations.keys())
        logger_module.log_relations(world.relations_matrix.relations, agents)
        analytics_results = analytics.compare_current_to_end(current_matrix)
       
        logger_module.log_analytics(analytics_results, analytics, current_matrix, step)

if __name__ == "__main__":
    # Initialize OpenAI client
    load_dotenv()
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Initialize mail system
    mail = Mail()

    # Load configuration
    script_dir = path.dirname(path.abspath(__file__))
    agents_file_path = path.join(script_dir, "config/agents.json")
    simulation_file_path = path.join(script_dir, "config/simulation.json")

    with open(agents_file_path) as f:
        agent_configs = json.load(f)

    with open(simulation_file_path) as f:
        simulation_config = json.load(f)
    use_full_identity = simulation_config.get("use_full_identity", False)

    # Load relations matrix
    relations_file_path = path.join(script_dir, "config/relations_start.json")
    relations_matrix = RelationsMatrix(relations_file_path)

    # Initialize custom logger
    logger_module.setup_logger(log_level=logging.DEBUG, log_file='simulation.log')

    # Initialize analytics with desired measures
    measures = {
        "MSE": measure_mse,
        "Cosine Similarity": measure_cosine_similarity,
        "Jaccard Similarity": measure_jaccard_similarity,
        "Pearson Correlation": measure_pearson_correlation
    }
    relations_end_file_path = path.join(script_dir, "config/relations_end.json")
    analytics = Analytics(relations_file_path, relations_end_file_path, measures, output_dir="output")

    # Create a dictionary mapping aliases to details (name and identity) for known entities
    known_entities = {agent["alias"]: {"name": agent["name"], "identity": agent["identity"]} for agent in agent_configs}

    # Initialize world
    world = World(
        agents=[
            Agent(
                alias=a["alias"],
                name=a["name"],
                agent_type=a["type"],
                identity=a["identity"],
                available_actions=a["available_actions"],
                military_power=a["military_power"],
                economic_power=a["economic_power"],
                goal=a["goal"],
                description=a["description"],
                client=client,
                use_full_identity=use_full_identity,
                known_entities=known_entities
            ) for a in agent_configs
        ],
        relations_matrix=relations_matrix,
        mail=mail,
        logger=logger_module,
        client=client
    )

    # Run simulation
    asyncio.run(simulation_loop(list(world.agents.values()), world, 5, analytics))
