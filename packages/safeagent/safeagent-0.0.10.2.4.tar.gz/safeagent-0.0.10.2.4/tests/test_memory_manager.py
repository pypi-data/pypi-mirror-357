# tests/test_memory_manager.py
import pytest
from unittest.mock import MagicMock
from safeagent.memory_manager import MemoryManager

# --- Tests for 'inmemory' backend ---

def test_inmemory_save_and_load():
    """Test saving and loading a value for a user."""
    memory = MemoryManager(backend="inmemory")
    user_id = "user1"
    key = "test_key"
    value = "test_value"

    memory.save(user_id, key, value)
    loaded_value = memory.load(user_id, key)

    assert loaded_value == value

def test_inmemory_load_missing_key():
    """Test that loading a non-existent key returns an empty string."""
    memory = MemoryManager(backend="inmemory")
    user_id = "user1"
    key = "non_existent_key"

    loaded_value = memory.load(user_id, key)

    assert loaded_value == ""

def test_inmemory_multiple_users():
    """Test that data for different users is kept separate."""
    memory = MemoryManager(backend="inmemory")
    user1, user2 = "user1", "user2"
    key = "data"
    value1, value2 = "user1_data", "user2_data"

    memory.save(user1, key, value1)
    memory.save(user2, key, value2)

    assert memory.load(user1, key) == value1
    assert memory.load(user2, key) == value2

def test_inmemory_summarize():
    """Test the summarization feature for the in-memory backend."""
    memory = MemoryManager(backend="inmemory")
    user_id = "summarize_user"
    
    # Mock LLM client
    mock_llm_client = MagicMock()
    mock_llm_client.generate.return_value = {"text": "This is a summary."}

    # Mock embedding function
    mock_embed_fn = MagicMock()

    memory.save(user_id, "msg1", "Hello there.")
    memory.save(user_id, "msg2", "How are you?")

    summary = memory.summarize(user_id, mock_embed_fn, mock_llm_client)

    assert summary == "This is a summary."
    # Verify the LLM was called with the concatenated text
    mock_llm_client.generate.assert_called_once()
    call_args = mock_llm_client.generate.call_args[0]
    assert "Hello there." in call_args[0]
    assert "How are you?" in call_args[0]
    
    # Verify the summary was saved back to memory
    assert memory.load(user_id, "summary") == "This is a summary."

# --- Optional: Tests for 'redis' backend (requires fakeredis) ---

try:
    import fakeredis
    redis_available = True
except ImportError:
    redis_available = False

@pytest.mark.skipif(not redis_available, reason="fakeredis is not installed")
def test_redis_save_and_load():
    """Test saving and loading using a fake redis backend."""
    # This setup mocks the redis client
    mock_redis_client = fakeredis.FakeStrictRedis()
    
    with pytest.MonkeyPatch.context() as m:
        # We patch 'from_url' to return our fake client
        m.setattr("redis.from_url", lambda url: mock_redis_client)
        
        memory = MemoryManager(backend="redis", redis_url="redis://dummy:1234")
        user_id = "redis_user"
        key = "redis_key"
        value = "redis_value"

        memory.save(user_id, key, value)
        loaded_value = memory.load(user_id, key)

        assert loaded_value == value
