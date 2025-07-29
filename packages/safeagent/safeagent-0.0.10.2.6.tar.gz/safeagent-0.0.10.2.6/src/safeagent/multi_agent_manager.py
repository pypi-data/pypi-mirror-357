# src/safeagent/multi_agent_manager.py
from typing import Dict, Any
from .stateful_orchestrator import StatefulOrchestrator
from .mcp import MessageBus, Message

class MultiAgentManager:
    """
    Manages a collection of agents and orchestrates their interaction
    via a central message bus.
    """
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self.agents: Dict[str, StatefulOrchestrator] = {}

    def add_agent(self, agent_id: str, agent_orchestrator: StatefulOrchestrator):
        """
        Adds an agent to the manager and registers it with the message bus.
        """
        self.agents[agent_id] = agent_orchestrator
        self.message_bus.register_agent(agent_id)
        print(f"Agent '{agent_id}' added to MultiAgentManager.")

    def run(self, initial_agent_id: str, inputs: Dict[str, Any], max_turns: int = 10):
        """
        Runs the multi-agent system.
        
        Args:
            initial_agent_id: The ID of the agent that starts the process.
            inputs: The initial inputs for the starting agent.
            max_turns: The maximum number of agent turns to prevent infinite loops.
        """
        print("\n--- Starting Multi-Agent Execution ---")
        current_agent = self.agents[initial_agent_id]
        current_agent.run(inputs=inputs)

        for turn in range(max_turns):
            print(f"\n--- Turn {turn + 1} ---")
            messages_in_flight = False
            for agent_id, agent in self.agents.items():
                incoming_messages = self.message_bus.get_messages(agent_id)
                if incoming_messages:
                    messages_in_flight = True
                    for msg in incoming_messages:
                        print(f"Invoking agent '{agent_id}' to handle message from '{msg.sender_id}'.")
                        agent.run(inputs={"message": msg.content, "request_id": msg.id})

            if not messages_in_flight:
                print("\n--- No more messages in flight. Execution finished. ---")
                break
        else:
            print("\n--- Max turns reached. Execution finished. ---")

