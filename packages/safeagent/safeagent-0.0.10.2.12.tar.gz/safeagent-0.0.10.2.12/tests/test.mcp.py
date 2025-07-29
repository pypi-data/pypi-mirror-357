# tests/test_mcp.py
import pytest
from safeagent import StatefulOrchestrator, ToolRegistry, GovernanceManager, AccessManager
from safeagent.mcp import MessageBus, Message
from safeagent.multi_agent_manager import MultiAgentManager

# Setup Mock Components

@pytest.fixture
def message_bus():
    """Provides a new MessageBus for each test."""
    return MessageBus()

@pytest.fixture
def governance_manager():
    """Provides a clean GovernanceManager instance."""
    # Corrected: Removed invalid 'log_to_file' argument.
    # The default constructor is sufficient for this test.
    return GovernanceManager()

@pytest.fixture
def access_manager():
    """Provides a default AccessManager."""
    return AccessManager()

# Test Agent Definitions

def create_research_agent(message_bus: MessageBus, governance_manager: GovernanceManager, access_manager: AccessManager) -> StatefulOrchestrator:
    """A researcher agent that can ask a database agent for information."""
    tool_registry = ToolRegistry(governance_manager=governance_manager, access_manager=access_manager)
    
    # Tool to SEND a message to another agent
    @tool_registry.register()
    def ask_database_agent(query: str) -> str:
        """Asks the database agent a question."""
        msg = Message(
            sender_id="research_agent",
            recipient_id="database_agent",
            content={"query": query}
        )
        message_bus.send_message(msg)
        return f"Message sent to database_agent with query: {query}"

    
    def research_node(state: dict) -> dict:
        # The user_id is needed to get a governed tool
        user_id = state.get("user_id", "research_user")
        research_tool = tool_registry.get_governed_tool("ask_database_agent", user_id=user_id)
        # In a real scenario, an LLM would decide to call this tool
        result = research_tool(query=state["message"])
        return {"status": result}

    orchestrator = StatefulOrchestrator(entry_node="research_node")
    orchestrator.add_node("research_node", research_node)
    orchestrator.add_edge("research_node", "__end__")
    return orchestrator

def create_database_agent(message_bus: MessageBus, governance_manager: GovernanceManager, access_manager: AccessManager) -> StatefulOrchestrator:
    """A database agent that answers queries and sends the response back."""
    tool_registry = ToolRegistry(governance_manager=governance_manager, access_manager=access_manager)

    # Tool to process a query and RESPOND
    @tool_registry.register()
    def query_database_and_respond(request: dict, request_id: str) -> str:
        """Queries the 'database' and sends a response message."""
        query = request.get("query")
        # Mock database lookup
        db_result = f"Data for '{query}'" if "SafeAgent" in query else "Data not found"
        
        response_msg = Message(
            sender_id="database_agent",
            recipient_id="research_agent",
            content={"data": db_result},
            is_response=True,
            request_id=request_id
        )
        message_bus.send_message(response_msg)
        return "Response sent."

    def db_node(state: dict) -> dict:
        user_id = state.get("user_id", "db_user")
        db_tool = tool_registry.get_governed_tool("query_database_and_respond", user_id=user_id)
        result = db_tool(request=state["message"], request_id=state["request_id"])
        return {"status": result}

    orchestrator = StatefulOrchestrator(entry_node="db_node")
    orchestrator.add_node("db_node", db_node)
    orchestrator.add_edge("db_node", "__end__")
    return orchestrator


# Verification Test

def test_agent_to_agent_communication(message_bus, governance_manager, access_manager):
    """
    Verify the full agent-to-agent communication loop.
    """
    # Create agents
    research_agent = create_research_agent(message_bus, governance_manager, access_manager)
    database_agent = create_database_agent(message_bus, governance_manager, access_manager)
    
    # Setup the Multi-Agent Manager
    manager = MultiAgentManager(message_bus)
    manager.add_agent("research_agent", research_agent)
    manager.add_agent("database_agent", database_agent)
    
    # The research_agent starts by asking a question.
    initial_inputs = {"message": "Tell me about SafeAgent v1", "user_id": "test_user"}
    manager.run(initial_agent_id="research_agent", inputs=initial_inputs)
    
    # Check the research_agent's mailbox for the response.
    final_messages = message_bus.get_messages("research_agent")
    assert len(final_messages) == 1
    response = final_messages[0]
    
    assert response.sender_id == "database_agent"
    assert response.content["data"] == "Data for 'Tell me about SafeAgent v1'"
    assert response.is_response is True
    print("\nTest passed: Agent-to-agent communication verified successfully.")
