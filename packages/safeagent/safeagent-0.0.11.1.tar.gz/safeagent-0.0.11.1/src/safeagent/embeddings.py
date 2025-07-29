import logging
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    requests = None

# A persistent session to reuse connections
if requests:
    _session = requests.Session()
else:
    # A dummy session if requests is not installed
    class _DummySession:
        def post(self, *args, **kwargs):
            raise ImportError("The 'requests' library is required for embeddings.")
    _session = _DummySession()


class EmbeddingError(Exception):
    """Custom exception for embedding-related failures."""
    pass


def gemini_embed(text: str, api_key: str, model: str = "embedding-001") -> Optional[List[float]]:
    """
    Generates embeddings using the Google Gemini API.

    This function now correctly formats the request for the embedding model,
    passing the API key as a URL parameter and avoiding conflicting headers.

    Args:
        text (str): The text to embed.
        api_key (str): The Google API key.
        model (str): The embedding model to use.

    Returns:
        A list of floats representing the embedding, or None on failure.
    
    Raises:
        EmbeddingError: If the API call fails after retries.
    """
    if not api_key:
        raise EmbeddingError("Gemini API key is required for embeddings.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent?key={api_key}"
    
    payload = {"model": f"models/{model}", "content": {"parts": [{"text": text}]}}
    
    headers = {"Content-Type": "application/json"}

    try:
        resp = _session.post(url, json=payload, headers=headers, timeout=30)
        
        if resp.status_code != 200:
            logging.error(f"Gemini embed API request failed with status {resp.status_code}: {resp.text}")
            raise EmbeddingError(f"Gemini embed failed: {resp.text}")

        data = resp.json()
        embedding = data.get("embedding", {}).get("values")

        if not embedding:
            raise EmbeddingError("Embedding not found in Gemini API response.")
            
        return embedding

    except requests.exceptions.RequestException as e:
        logging.error(f"A network error occurred while calling Gemini embed API: {e}")
        raise EmbeddingError(f"Network error during embedding: {e}") from e