# Coalitions Simulation

## Overview
The **Coalitions Simulation** is a multi-agent simulation framework that models how political and military entities interact in conflict zones. It uses OpenAI's language models to let agents make decisions, send messages, form alliances, and take military action, all driven by each agent’s unique objectives, identities, and inter-relationships.

## The Problem We’re Solving
Real-world interventions in Iraq, Afghanistan, and Libya underscore the dangers of misjudging complex post-conflict environments. Conventional planning often overlooks how cultural, religious, or ideological factors shape on-the-ground alliances, leading to unforeseen outcomes.

**Why This Matters**  
- **Fewer Surprises**: Anticipate how different groups might shift or align before committing resources and lives.  
- **Objective Insights**: LLMs can simulate varied perspectives, minimizing the biases that policymakers sometimes project.  
- **Early Success**: Even this minimal prototype accurately recreated key coalition formations from the 2014 war against ISIS.  
- **Smarter Planning**: A more advanced simulator can help planners foresee unintended consequences, avoid costly missteps, and potentially avert conflicts that might not resolve as intended.


This repository offers a **prototype** that showcases how LLM-based agent simulations can sharpen post-conflict planning and decision-making. By accurately modeling alliance shifts and cultural factors in advance, we can avert the kinds of unintended outcomes that have cost trillions of dollars—and countless lives. Future enhancements could turn this prototype into a robust forecasting tool, helping policymakers devise more effective, peace-oriented strategies.  


## Features

- **Multi-Agent System**: Simulates interactions between diverse agents, including militant groups, nation-states, regional forces, and coalition forces.
- **Dynamic Decision-Making**: Agents make decisions based on their goals, current state, and relationships with other agents.
- **Relationship Management**: Models alliances, conflicts, and neutral relations, dynamically adjusting based on interactions.
- **Asynchronous Execution**: Utilizes Python's `asyncio` to run simulations efficiently and handle multiple agent interactions concurrently.
- **Customizable Scenarios**: Easily configure different scenarios, agent attributes, and initial conditions through JSON configuration files.
- **Analytics and Metrics**: Provides tools to analyze the simulation results, including measures like MSE and Cosine Similarity.

## Getting Started

This project **requires Python 13**. If you already have Python 13 installed, you can proceed with a straightforward setup. If not, we recommend using [**uv**](https://docs.astral.sh/uv/getting-started/) to download and manage Python versions locally.

---

### Prerequisites
- **OpenAI API Key** (for GPT-4 or another model)
- **Python 13** installed locally  
  *OR*  
- **uv** (to manage and install Python 13 automatically)  

### Installation

 **Clone this repository**:
   ```bash
   git clone https://github.com/skrivov/coalitions.git
   cd coalitions
   ```

 **Add your OpenAI API key by creating a `.env` file in the project root**:
   ```bash
  OPENAI_API_KEY=your_api_key_here
   ```

### Option A: If You Already Have Python 13

1. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows:  venv\Scripts\activate
   ```
3. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the simulation**:
   ```bash
   python main.py
   ```

## Option B: If You Need to Install Python 13 

1. **Install `uv`**:

   - **macOS and Linux**:
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```

   - **Windows**:
     Open PowerShell and run:
     ```powershell
     irm https://astral.sh/uv/install.ps1 | iex
     ```
     [other installation options](https://docs.astral.sh/uv/getting-started/installation/)

2. **Install Python 13 using `uv`**:
    ```bash
   uv python install 3.13
   ```
3. **Create and activate a virtual environment with Python 13**:
   ```bash
       uv venv --python 3.13
       source .venv/bin/activate  # On Windows: venv\Scripts\activate
     ```
4. **Install the required packages**:
   ```bash
   uv sync

   ```

5. **Run the simulation**:
   ```bash
   python main.py
   ```
[see uv docs](https://docs.astral.sh/uv/getting-started/)


 ##  Output
The simulation logs details of each step, including agent actions, state updates, and messages exchanged, to both the console and a log file [simulation.log](simulation.log). Analytical metrics are also provided at each step.