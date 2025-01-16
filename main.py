"""
main.py

Entry point for running the entire simulation: initializes agents, loads configurations,
runs the simulation loop, and performs analytics.
"""

from __future__ import annotations
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
from analytics import Analytics, measure_mse, measure_cosine_similarity
import custom_logger as logger_module

# Number os simulation steps
NUM_STEPS = 7

async def simulation_loop(
    agents: list[Agent],
    world: World,
    rounds: int,
    analytics: Analytics
) -> None:
    """
    The main simulation loop, orchestrating agent actions, message exchanges, and analytics.

    Args:
        agents (list[Agent]): A list of agents participating in the simulation.
        world (World): The simulation world that maintains states and relations.
        rounds (int): The number of simulation rounds to execute.
        analytics (Analytics): The analytics object used to compare the simulation progress.
    """
    logger_module.log_agents_intro(agents)
    logger_module.log_relations(world.relations_matrix.relations, agents)

    for step in range(rounds):
        # Record the state of the world at the start of each round
        world.record_state()

        # Step 1: Agents read public statements and private messages, decide on sending new messages
        public_statements = world.mail.read_public_statements()
        message_tasks = [
            agent.decide_and_send_messages(
                json.dumps(world.get_current_state()),
                json.dumps([message.to_dict() for message in agent.read_messages(world.mail)]),
                json.dumps([statement.to_dict() for statement in public_statements]),
                world.relations_matrix.relations
            ) for agent in agents
        ]
        messages_list = await asyncio.gather(*message_tasks)

        # Send out all decided messages
        for agent_obj, messages in zip(agents, messages_list):
            for message in messages:
                world.mail.send(message)

        # Log the messages that were sent
        logger_module.log_messages([msg for messages in messages_list for msg in messages])

        # Step 2: Agents take actions based on the world state
        action_tasks = [
            agent.act(
                json.dumps(world.get_current_state()),
                json.dumps([message.to_dict() for message in agent.read_messages(world.mail)]),
                json.dumps([statement.to_dict() for statement in public_statements])
            )
            for agent in agents
        ]
        latest_actions = await asyncio.gather(*action_tasks)

        # Add these actions to the current state
        for agent_obj, action in zip(agents, latest_actions):
            world.add_action(agent_obj.alias, action)

        # Log the actions taken
        logger_module.log_actions(latest_actions)

        # Step 3: Finalize messages and public statements
        world.mail.finalize()

        # Step 4: Process private messages and public statements
        world.process_messages()
        world.process_public_statements(public_statements)

        # Step 5: Apply outcomes/updates based on the decisions
        updates = await world.decide(latest_actions)
        world.apply_updates(updates)
        logger_module.log_agent_state(agents)

        # Step 6: Log and compare current matrix to the end matrix
        current_matrix = world.relations_matrix.to_matrix(
            list(world.relations_matrix.relations.keys())
        )
        logger_module.log_relations(world.relations_matrix.relations, agents)
        analytics_results = analytics.compare_current_to_end(current_matrix)
        logger_module.log_analytics(analytics_results, analytics, current_matrix, step)


def main() -> None:
    """
    Main entry point for setting up the simulation environment, loading configurations,
    and running the event loop to drive the simulation.
    """
    load_dotenv()
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    mail = Mail()

    script_dir = path.dirname(path.abspath(__file__))
    agents_file_path = path.join(script_dir, "config/agents.json")
    simulation_file_path = path.join(script_dir, "config/simulation.json")

    with open(agents_file_path, "r", encoding="utf-8") as f:
        agent_configs = json.load(f)

    with open(simulation_file_path, "r", encoding="utf-8") as f:
        simulation_config = json.load(f)
    use_full_identity = simulation_config.get("use_full_identity", False)

    relations_file_path = path.join(script_dir, "config/relations_start.json")
    relations_matrix = RelationsMatrix(relations_file_path)

    logger_module.setup_logger(log_level=logging.DEBUG, log_file="simulation.log")

    measures = {
        "MSE": measure_mse,
        "Cosine Similarity": measure_cosine_similarity
        # You can add more measures here if desired
    }
    relations_end_file_path = path.join(script_dir, "config/relations_end.json")
    analytics = Analytics(relations_file_path, relations_end_file_path, measures, output_dir="output")

    known_entities = {
        agent_cfg["alias"]: {
            "name": agent_cfg["name"],
            "identity": agent_cfg["identity"]
        } for agent_cfg in agent_configs
    }

    # Initialize all agents
    agents = [
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
        )
        for a in agent_configs
    ]

    # Create the World
    world = World(
        agents=agents,
        relations_matrix=relations_matrix,
        mail=mail,
        logger=logger_module,
        client=client
    )

    # Run the simulation asynchronously
    asyncio.run(simulation_loop(agents, world, NUM_STEPS, analytics))


if __name__ == "__main__":
    main()
