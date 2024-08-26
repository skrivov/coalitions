# custom_logger.py
import logging

# Set up the logger
logger = logging.getLogger(__name__)

def setup_logger(log_level=logging.INFO, log_file=None):
    """
    Set up the logger with a specified level and optionally a log file.
    
    Args:
    - log_level (int): The logging level (e.g., logging.DEBUG, logging.INFO).
    - log_file (str): The path to a log file. If None, logs will be printed to the console.
    """
    # Define the log format
    formatter = logging.Formatter(' %(message)s')

    # Create handlers
    if log_file:
        # Log to a file with mode 'w' to overwrite the file on each run
        file_handler = logging.FileHandler(log_file, mode='w')  # Overwrite mode
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.setLevel(log_level)

def log_agents_intro(agents):
    logger.info("Introduction of agents:")
    for agent in agents:
        logger.info(f"Alias: {agent.alias}, Name: {agent.name}, Identity: {agent.identity}")

def log_relations(relations, agents):
    logger.info("Relations Matrix:")
    agent_aliases = [agent.alias for agent in agents]
    headers, table = to_user_friendly_format(relations, agent_aliases)

    # Determine column width for better alignment
    column_width = max(len(alias) for alias in agent_aliases) + 2  # Adding padding for readability

    # Format headers
    header_line = "".join(f"{header:>{column_width}}" for header in headers)
    logger.info(header_line)

    # Format each row in the table
    for row in table:
        row_line = "".join(f"{str(item):>{column_width}}" for item in row)
        logger.info(row_line)

def to_user_friendly_format(relations, agent_aliases):
    headers = [""] + agent_aliases
    table = [[agent] + [relations[agent][other] for other in agent_aliases] for agent in agent_aliases]
    return headers, table

def log_agent_state(agents):
    logger.info("Agents' State Variables:")
    for agent in agents:
        # Format the military and economic power to one decimal place
        logger.info(f"{agent.alias} - Military Power: {agent.military_power:.1f}, Economic Power: {agent.economic_power:.1f}")

def log_messages(messages):
    logger.info("Messages Sent:")
    for message in messages:
        # Truncate content to 50 characters and add ellipsis if needed
        truncated_content = (message.content[:97] + '...') if len(message.content) > 100 else message.content
        logger.info(f"Type: {message.message_type}, From: {message.sender}, To: {message.recipient}, Content: {truncated_content}")

def log_actions(actions):
    logger.info("Actions Taken:")
    for action in actions:
        logger.info(f"Agent: {action.subject}, Action: {action.action}, Object: {action.object}")

def log_analytics(analytics_results, analytics, current_matrix, step):
    for measure_name, value in analytics_results.items():
        logger.info(f"{measure_name}: {value:.2f}")
    analytics.visualize_matrices(current_matrix, step)
