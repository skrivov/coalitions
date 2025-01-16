"""
custom_logger.py

Provides custom logging functionality for the simulation, including
logging agent introductions, actions, messages, and analytics.
"""

from __future__ import annotations

import logging
from agent import Agent
from message import Message
from action import Action
from analytics import Analytics

logger = logging.getLogger(__name__)


def setup_logger(log_level: int = logging.INFO, log_file: str | None = None) -> None:
    """
    Sets up the logger with a specified level and an optional log file.

    Args:
        log_level: The logging level (e.g., logging.DEBUG, logging.INFO).
        log_file: The path to a log file. If None, logs go to the console.
    """
    formatter = logging.Formatter(" %(message)s")

    # If a log file is specified, write logs to that file (overwriting each run).
    if log_file is not None:
        file_handler = logging.FileHandler(log_file, mode="w")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Always log to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.setLevel(log_level)


def log_agents_intro(agents: list[Agent]) -> None:
    """
    Logs an introduction for each agent.

    Args:
        agents: The list of agent objects to log.
    """
    logger.info("Introduction of agents:")
    for agent in agents:
        logger.info(f"Alias: {agent.alias}, Name: {agent.name}, Identity: {agent.identity}")


def log_relations(relations: dict[str, dict[str, int]], agents: list[Agent]) -> None:
    """
    Logs the relations matrix in a user-friendly format.

    Args:
        relations: The current relations data.
        agents: The list of agents to derive ordering and references from.
    """
    logger.info("Relations Matrix:")
    agent_aliases = [agent.alias for agent in agents]
    headers, table = to_user_friendly_format(relations, agent_aliases)

    # Determine column width for better alignment
    column_width = max(len(alias) for alias in agent_aliases) + 2

    # Format headers
    header_line = "".join(f"{header:>{column_width}}" for header in headers)
    logger.info(header_line)

    # Format each row in the table
    for row in table:
        row_line = "".join(f"{str(item):>{column_width}}" for item in row)
        logger.info(row_line)


def to_user_friendly_format(
    relations: dict[str, dict[str, int]],
    agent_aliases: list[str]
) -> tuple[list[str], list[list[str | int]]]:
    """
    Converts relations data to a user-friendly header and table format.

    Args:
        relations: The relations matrix data.
        agent_aliases: Ordered list of agent aliases to include.

    Returns:
        A tuple containing the headers and a table of row data for logging.
    """
    headers = [""] + agent_aliases
    table = [
        [agent] + [relations[agent][other] for other in agent_aliases]
        for agent in agent_aliases
    ]
    return headers, table


def log_agent_state(agents: list[Agent]) -> None:
    """
    Logs the current state (military and economic power) of each agent.

    Args:
        agents: The list of agents.
    """
    logger.info("Agents' State Variables:")
    for agent in agents:
        logger.info(
            f"{agent.alias} - Military Power: {agent.military_power:.1f}, "
            f"Economic Power: {agent.economic_power:.1f}"
        )


def log_messages(messages: list[Message]) -> None:
    """
    Logs the messages that were sent.

    Args:
        messages: The list of messages to log.
    """
    logger.info("Messages Sent:")
    for message in messages:
        truncated_content = (
            message.content[:97] + "..."
            if len(message.content) > 100
            else message.content
        )
        logger.info(
            f"Type: {message.message_type}, From: {message.sender}, "
            f"To: {message.recipient}, Content: {truncated_content}"
        )


def log_actions(actions: list[Action]) -> None:
    """
    Logs the actions taken by agents.

    Args:
        actions: The list of actions to log.
    """
    logger.info("Actions Taken:")
    for action in actions:
        logger.info(
            f"Agent: {action.subject}, Action: {action.action}, Object: {action.object}"
        )


def log_analytics(
    analytics_results: dict[str, float],
    analytics: Analytics,
    current_matrix: list[list[int]],
    step: int
) -> None:
    """
    Logs analytics results and produces a matrix visualization for the current step.

    Args:
        analytics_results: The computed metrics comparing current and end-state matrices.
        analytics: An Analytics object capable of generating matrix visualizations.
        current_matrix: The current state matrix to visualize.
        step: The current simulation step index.
    """
    for measure_name, value in analytics_results.items():
        logger.info(f"{measure_name}: {value:.2f}")
    analytics.visualize_matrices(current_matrix, step)
