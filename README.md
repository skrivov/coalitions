# Coalitions Simulation

## Overview

The Coalitions Simulation is a multi-agent simulation framework designed to model the dynamic interactions between various political and military entities in a conflict zone. This simulation leverages OpenAI's language models to enable agents to make decisions, send messages, form alliances, and engage in military actions based on their objectives, identities, and relationships with other entities.

## Features

- **Multi-Agent System**: Simulates interactions between diverse agents, including militant groups, nation-states, regional forces, and coalition forces.
- **Dynamic Decision-Making**: Agents make decisions based on their goals, current state, and relationships with other agents.
- **Relationship Management**: Models alliances, conflicts, and neutral relations, dynamically adjusting based on interactions.
- **Asynchronous Execution**: Utilizes Python's `asyncio` to run simulations efficiently and handle multiple agent interactions concurrently.
- **Customizable Scenarios**: Easily configure different scenarios, agent attributes, and initial conditions through JSON configuration files.
- **Analytics and Metrics**: Provides tools to analyze the simulation results, including measures like MSE, Cosine Similarity, Jaccard Similarity, and Pearson Correlation.

## Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API Key (for accessing GPT-4 or other models)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/skrivov/coalitions.git
   cd coalitions
   ```
2. **Create a virtual environment and activate it:**
   ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
   ```
3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```
   
4. **Set up your OpenAI API key:** 
 Create a .env file in the project root and add your OpenAI API key:

   ```bash
    OPENAI_API_KEY=your_api_key_here
   ```
## Running the Simulation
To run the simulation, execute:
 ```bash
    python main.py
   ```



 ##  Output
The simulation logs details of each step, including agent actions, state updates, and messages exchanged, to both the console and a log file (simulation.log). Analytical metrics are also provided at each step.