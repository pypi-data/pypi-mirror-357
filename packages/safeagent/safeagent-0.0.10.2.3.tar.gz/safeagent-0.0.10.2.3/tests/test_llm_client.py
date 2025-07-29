# tests/test_llm_client.py
import pytest
import requests
from unittest.mock import patch, MagicMock
from safeagent.llm_client import LLMClient, FrameworkError

@patch('safeagent.llm_client.requests.Session')
def test_llm_client_generate_gemini_success(MockSession):
    """Test a successful generate call to the Gemini provider."""
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [{
            "content": {
                "parts": [{"text": "Gemini says hello"}]
            }
        }],
        "usageMetadata": {
            "promptTokenCount": 10,
            "candidatesTokenCount": 5
        }
    }
    mock_session_instance = MockSession.return_value
    mock_session_instance.post.return_value = mock_response

    client = LLMClient(provider="gemini", api_key="fake-gemini-key", model="gemini-pro")

    # Act
    result = client.generate("A prompt")

    # Assert
    assert result["text"] == "Gemini says hello"
    assert result["usage"]["prompt_tokens"] == 10
    assert result["usage"]["completion_tokens"] == 5
    mock_session_instance.post.assert_called_once()
    call_args = mock_session_instance.post.call_args
    assert "https://generativelanguage.googleapis.com" in call_args[0][0]
    assert "fake-gemini-key" in call_args[0][0]


@patch('safeagent.llm_client.requests.Session')
def test_llm_client_generate_openai_success(MockSession):
    """Test a successful generate call to the OpenAI provider."""
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": "OpenAI says hello"
            }
        }],
        "usage": {
            "prompt_tokens": 12,
            "completion_tokens": 8
        }
    }
    mock_session_instance = MockSession.return_value
    mock_session_instance.post.return_value = mock_response

    client = LLMClient(provider="openai", api_key="fake-openai-key", model="gpt-4")

    # Act
    result = client.generate("A prompt")

    # Assert
    assert result["text"] == "OpenAI says hello"
    assert result["usage"]["prompt_tokens"] == 12
    assert result["usage"]["completion_tokens"] == 8
    mock_session_instance.post.assert_called_once()
    # Check that the auth header was set correctly
    assert mock_session_instance.headers["Authorization"] == "Bearer fake-openai-key"


@patch('safeagent.llm_client.requests.Session')
def test_llm_client_handles_http_error_with_retries(MockSession):
    """Test that the client retries on HTTP failure and then raises an error."""
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    
    mock_session_instance = MockSession.return_value
    mock_session_instance.post.return_value = mock_response

    client = LLMClient(provider="openai", api_key="fake-key", model="gpt-4")
    
    # Act & Assert
    with patch('time.sleep') as mock_sleep: # Mock sleep to speed up test
        with pytest.raises(FrameworkError) as excinfo:
            client.generate("A prompt")
        
        # Verify it was called 3 times (1 initial + 2 retries)
        assert mock_session_instance.post.call_count == 3
        assert "LLM generate() failed after 3 attempts" in str(excinfo.value)
        # Verify exponential backoff was attempted
        assert mock_sleep.call_count == 2


@patch('safeagent.llm_client.requests.Session')
def test_llm_client_retry_on_network_error_then_succeeds(MockSession):
    """Test that the client retries on a network error and succeeds on the second attempt."""
    # Arrange
    mock_success_response = MagicMock()
    mock_success_response.status_code = 200
    mock_success_response.json.return_value = {
        "choices": [{"message": {"content": "Success!"}}],
        "usage": {}
    }

    mock_session_instance = MockSession.return_value
    mock_session_instance.post.side_effect = [
        requests.exceptions.Timeout("Connection timed out"), 
        mock_success_response
    ]

    client = LLMClient(provider="openai", api_key="fake-key", model="gpt-4")

    # Act
    with patch('time.sleep') as mock_sleep:
        result = client.generate("A prompt")

    # Assert
    assert result["text"] == "Success!"
    assert mock_session_instance.post.call_count == 2
    mock_sleep.assert_called_once_with(1) # 2**0
