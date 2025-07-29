# tests/test_tool_registry.py
import pytest
import time
from unittest.mock import MagicMock, patch
from safeagent import ToolRegistry, GovernanceManager, AccessManager
from safeagent.sinks import BaseOutputSink
from rbac import RBACError # Correct exception type

@pytest.fixture
def governance_manager():
    """Provides a mock GovernanceManager."""
    return MagicMock(spec=GovernanceManager)

@pytest.fixture
def access_manager():
    """Provides a mock AccessManager."""
    return MagicMock(spec=AccessManager)

@pytest.fixture
def tool_registry(governance_manager, access_manager):
    """Provides a ToolRegistry with mocked dependencies."""
    # Mock the embedding call to avoid actual API calls
    with patch('safeagent.tool_registry.gemini_embed') as mock_embed:
        mock_embed.return_value = [0.1] * 768 # Dummy embedding
        registry = ToolRegistry(
            governance_manager=governance_manager,
            access_manager=access_manager
        )
        yield registry

def test_tool_registration_and_schema_generation(tool_registry):
    """Verify that a tool is registered and its schema is correctly generated."""
    @tool_registry.register()
    def sample_tool(name: str, age: int) -> str:
        """A simple tool for testing."""
        return f"Hello, {name}! You are {age}."

    # Corrected: Method is generate_tool_schema and takes a list
    schemas = tool_registry.generate_tool_schema(["sample_tool"])
    
    assert isinstance(schemas, list)
    assert len(schemas) == 1
    schema = schemas[0]

    assert schema["name"] == "sample_tool"
    assert "A simple tool for testing" in schema["description"]
    assert "name" in schema["parameters"]["properties"]
    assert schema["parameters"]["properties"]["name"]["type"] == "string"
    assert "age" in schema["parameters"]["properties"]
    # Corrected: JSON schema type for integer is 'number'
    assert schema["parameters"]["properties"]["age"]["type"] == "number"
    assert "name" in schema["parameters"]["required"]
    assert "age" in schema["parameters"]["required"]


def test_rbac_policy_enforced(tool_registry, access_manager):
    """Verify that the RBAC policy correctly grants or denies access."""
    @tool_registry.register(required_role="admin")
    def protected_tool():
        return "Access granted"

    # Test with access GRANTED
    access_manager.check_access.return_value = True
    admin_tool = tool_registry.get_governed_tool(name="protected_tool", user_id="admin_user")
    assert admin_tool() == "Access granted"
    access_manager.check_access.assert_called_with("admin_user", "admin")

    # Test with access DENIED
    access_manager.check_access.return_value = False
    with pytest.raises(RBACError) as excinfo: # Correct exception
        # get_governed_tool returns a callable; the error is raised on call
        non_admin_tool = tool_registry.get_governed_tool(name="protected_tool", user_id="basic_user")
        non_admin_tool()
    assert "lacks required role 'admin'" in str(excinfo.value)

def test_retry_policy_on_failure(tool_registry):
    """Verify that the tool is retried on failure."""
    mock_tool_logic = MagicMock()
    mock_tool_logic.side_effect = [ValueError("Failed!"), "Success!"]

    @tool_registry.register(retry_attempts=1, retry_delay=0.01)
    def flaky_tool():
        return mock_tool_logic()
    
    with patch('time.sleep'): # Avoid actual sleep
        governed_tool = tool_registry.get_governed_tool("flaky_tool", user_id="test_user")
        result = governed_tool()

    assert result == "Success!"
    assert mock_tool_logic.call_count == 2

def test_caching_policy(tool_registry):
    """Verify that tool results are cached and served from cache."""
    mock_tool_logic = MagicMock(return_value="Expensive result")

    @tool_registry.register(cache_ttl_seconds=60)
    def expensive_tool(param: int):
        return mock_tool_logic(param)
    
    # Corrected: get_governed_tool needs a user_id
    governed_tool = tool_registry.get_governed_tool("expensive_tool", user_id="test_user")

    # First call - should execute the tool
    result1 = governed_tool(param=123)
    assert result1 == "Expensive result"
    assert mock_tool_logic.call_count == 1

    # Second call with same params - should be served from cache
    result2 = governed_tool(param=123)
    assert result2 == "Expensive result"
    assert mock_tool_logic.call_count == 1 # Should not have increased

    # Third call with different params - should execute the tool again
    result3 = governed_tool(param=456)
    assert result3 == "Expensive result"
    assert mock_tool_logic.call_count == 2

def test_output_sinks_are_called(tool_registry, governance_manager):
    """Verify that output sinks are called with the tool's result."""
    # Use a real mock object that inherits from the base class
    mock_sink = MagicMock(spec=BaseOutputSink)
    mock_sink.handle.return_value = {"status": "success"}
    governance_manager.get_current_run_id.return_value = "run_123"

    @tool_registry.register(output_sinks=[mock_sink])
    def tool_with_sink(name: str):
        return f"Output for {name}"

    governed_tool = tool_registry.get_governed_tool("tool_with_sink", user_id="test_user")
    result = governed_tool(name="test")

    # Corrected: Assert that 'handle' was called with the correct signature
    mock_sink.handle.assert_called_once()
    call_args, call_kwargs = mock_sink.handle.call_args
    assert call_args[0] == "tool_with_sink"  # tool_name
    assert call_args[1] == "Output for test" # result
    assert call_args[2] == "run_123"         # run_id
    assert call_kwargs == {"name": "test"}   # original kwargs
