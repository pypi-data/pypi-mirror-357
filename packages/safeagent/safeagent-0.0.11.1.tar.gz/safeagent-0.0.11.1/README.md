# SafeAgent

[![PyPI version](https://badge.fury.io/py/safeagent.svg)](https://badge.fury.io/py/safeagent)
[![Build Status](https://github.com/ViktorVeselov/SafeAgent/actions/workflows/publish-to-pypi.yml/badge.svg)](https://github.com/ViktorVeselov/SafeAgent/actions/workflows/publish-to-pypi.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://viktorveselov.github.io/SafeAgent/)
[![Downloads](https://pepy.tech/badge/SafeAgent)](https://pepy.tech/project/SafeAgent)

**safeagent** is a framework for building stateful, graph-based language model agents with enterprise-grade governance, reliability, and observability built-in from day one. It provides low-level building blocks for creating individual tools and stateful graphs, and a high-level `ProtocolManager` to run complete, multi-step agent workflows.

## Core Benefits

* **Protocols**: Run complex agents using different execution strategies. Use the Master/Controller/Program (`MCP`) protocol for advanced tool use and retrieval, or define custom multi-agent interactions with the `AGENT2AGENT` protocol.
* **Graphs**: Go beyond simple chains and build complex, cyclical agents with conditional logic that can reason and adapt using the `StatefulOrchestrator`.
* **Governance & Observability**: Every action—from protocol execution to node transitions—is automatically audited with detailed logs for cost, latency, and data lineage.
* **Reliability**: Build resilient tools with built-in policies for caching, automatic retries with exponential backoff, and circuit breakers.
* **Human-in-the-Loop**: Pause a stateful graph at any point, allow for human review or input, and seamlessly resume the workflow.
* **Extensible Sinks**: Automatically send tool results to other systems like files, databases, or message queues (e.g., Pub/Sub) for seamless integration.

## Get Started

### Installation

For local development, clone the repository and install in editable mode:

```bash
git clone [https://github.com/ViktorVeselov/SafeAgent.git](https://github.com/ViktorVeselov/SafeAgent.git)
cd SafeAgent
pip install -e .
```

### Example 1: A Production-Ready Tool

This example demonstrates how to create a standalone tool with a rich set of declarative policies, including cost tracking, caching, retries, and output sinks.

#### Imports and Setup

```python
import os
import shutil
from pathlib import Path
from safeagent import ToolRegistry, GovernanceManager, AccessManager
from safeagent.sinks import FileOutputSink, PubSubSink

# Initialize the Governance Manager to track all actions
gov = GovernanceManager()
# The system will look up the user's roles from here.
access_manager = AccessManager(role_config={
    "user_viktor": ["billing_agent", "support"]
})

# Define sinks to handle tool outputs
file_sink = FileOutputSink(base_path="invoices")
pubsub_sink = PubSubSink(project_id="your-gcp-project", topic_id="invoice-notifications")
```

#### Define a Governed Tool with `@register`

The `@register` decorator is the heart of `safeagent`'s power. Here, we define a tool and attach several production-grade policies directly to it.

```python
# The ToolRegistry uses the GovernanceManager and AccessManager
tool_registry = ToolRegistry(
    governance_manager=gov,
    access_manager=access_manager
)

# This cost function calculates a dynamic cost based on the tool's output.
def calculate_invoice_cost(result):
    return 0.05 if result.get("status") == "success" else 0.01

@tool_registry.register(
    required_role="billing_agent",
    retry_attempts=2,
    retry_delay=1.5,
    cache_ttl_seconds=3600,
    cost_calculator=calculate_invoice_cost,
    output_sinks=[file_sink, pubsub_sink]
)
def generate_invoice(customer_id: int, amount: float) -> dict:
    """
    Generates a new invoice for a customer and saves it.
    This tool is restricted to users with the 'billing_agent' role.
    """
    invoice_data = {"customerId": customer_id, "amount": amount, "status": "success"}
    return invoice_data
```

#### Execute the Tool

When we get the tool from the registry, it's already wrapped with all the policies we defined. Executing it automatically triggers all associated governance.

```python
# The AccessManager will verify if "user_viktor" has the required role.
governed_invoice_tool = tool_registry.get_governed_tool(
    name="generate_invoice",
    user_id="user_viktor"
)

# Execute the tool. This will trigger RBAC checks, retries, cost calculation, and sinks.
result = governed_invoice_tool(customer_id=456, amount=199.99)

# Clean up the generated directory for the example
shutil.rmtree("invoices", ignore_errors=True)
```

### Example 2: A Stateful Research Agent

This example shows how to use governed tools within the `StatefulOrchestrator` to build a complex, multi-step agent with conditional logic.

```python
from safeagent import StatefulOrchestrator, ToolRegistry, GovernanceManager
from safeagent.sinks import FileOutputSink

# We can use the same GovernanceManager from the previous example
gov = GovernanceManager()
tool_registry_agent = ToolRegistry(governance_manager=gov)
file_sink_agent = FileOutputSink(base_path="research_outputs")

@tool_registry_agent.register(cache_ttl_seconds=3600, output_sinks=[file_sink_agent])
def conduct_research(topic: str) -> str:
    """Conducts research on a given topic."""
    print(f"--- Conducting research on: {topic} ---")
    if "gemini" in topic.lower():
        return "Gemini is a family of multimodal models developed by Google."
    return "No information found."

@tool_registry_agent.register(output_sinks=[file_sink_agent])
def write_summary(research_data: str) -> str:
    """Writes a summary based on the provided research data."""
    print(f"--- Writing summary for: {research_data[:30]}... ---")
    return f"Summary: {research_data}"

# Get the governed tools with a user_id
research_tool = tool_registry_agent.get_governed_tool("conduct_research", user_id="agent_user")
summary_tool = tool_registry_agent.get_governed_tool("write_summary", user_id="agent_user")

# Define Graph Nodes
def research_node(state: dict) -> dict:
    research_result = research_tool(topic=state["topic"])
    return {"research_data": research_result}

def summary_node(state: dict) -> dict:
    summary_result = summary_tool(research_data=state["research_data"])
    return {"summary": summary_result}

# Define a Conditional Edge
def decide_next_step(state: dict) -> str:
    if state.get("research_data") and "No information found" not in state["research_data"]:
        return "summary_node"
    return "__end__"

# Build and Run the Graph
orchestrator = StatefulOrchestrator(entry_node="research_node")
orchestrator.add_node("research_node", research_node)
orchestrator.add_node("summary_node", summary_node)
orchestrator.add_conditional_edge("research_node", decide_next_step)
orchestrator.add_edge("summary_node", "__end__")

# Run the graph
status, final_state = orchestrator.run(inputs={"topic": "Google Gemini"})
print(f"\nGraph execution finished with status: {status}")

shutil.rmtree("research_outputs", ignore_errors=True)
```

### Example 3: A Complete Agent with ProtocolManager (Recommended)

This example shows the primary, high-level way to run a complete agent using the `ProtocolManager`. It handles initializing all the necessary components and running a full pipeline.

```python
from safeagent import ProtocolManager, PROTOCOLS, AccessManager
from pathlib import Path

# Define user roles
custom_roles = {
    "weather_user_01": ["vector_store", "llm_call", "weather_forecaster"]
}
access_manager = AccessManager(role_config=custom_roles)

# Set up dummy templates for the agent to use
Path("templates").mkdir(exist_ok=True)
(Path("templates") / "tool_decider_prompt.j2").write_text("Question: {{ question }}\nTools: {{ tools }}")
(Path("templates") / "synthesis_prompt.j2").write_text("Synthesize a final answer from this tool result: {{ tool_result }}")


# Instantiate the ProtocolManager for the MCP protocol
# This manager will automatically build an agent that can reason about
# when to use tools.
pm = ProtocolManager(
    protocol=PROTOCOLS.MCP.value,
    access_manager=access_manager
)

# Define the inputs for the agent run
agent_inputs = {
    "user_input": "What is the weather like in San Francisco?",
    "user_id": "weather_user_01",
}

# Run the agent
# Note: Requires GEMINI_API_KEY environment variable to be set.
final_results = pm.run(agent_inputs)

print("\n--- ProtocolManager Final Result ---")
# The final answer is found in the 'generate_final_answer' node's output
print(final_results.get("generate_final_answer", {}).get("text"))
```

After running these scripts, you will see a detailed `audit.log` file with every action, cost, and policy decision, providing complete visibility into your agent's operations.

## Documentation

For more information, see the **[Quickstart](https://www.google.com/search?q=https://viktorveselov.github.io/SafeAgent/quickstart/)** for details, or browse the **[full documentation site](https://viktorveselov.github.io/SafeAgent/)**.
