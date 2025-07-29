# tests/test_retriever.py
import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from pathlib import Path

# Mock faiss before importing the retriever
faiss_mock = MagicMock()

# Configure the mock to behave like the faiss library
mock_index_instance = MagicMock()
faiss_mock.IndexFlatL2.return_value = mock_index_instance
faiss_mock.read_index.return_value = mock_index_instance

with patch.dict('sys.modules', {'faiss': faiss_mock}):
    from safeagent.retriever import VectorRetriever

@pytest.fixture
def mock_embed_fn():
    """Fixture to create a mock embedding function."""
    # This function returns a vector based on the length of the text
    return MagicMock(side_effect=lambda text: np.array([len(text) * 0.1] * 768, dtype=np.float32))

@pytest.fixture
def retriever(tmp_path, mock_embed_fn):
    """Fixture to create a VectorRetriever with a temporary index path."""
    index_path = str(tmp_path / "test.index")
    # Ensure the index file does not exist initially for a clean test
    Path(index_path).unlink(missing_ok=True)
    return VectorRetriever(index_path=index_path, embed_model_fn=mock_embed_fn)

def test_retriever_initialization(retriever, mock_embed_fn):
    """Test that the VectorRetriever initializes correctly."""
    assert retriever.embed == mock_embed_fn
    assert retriever._index is not None # Should be initialized to a mock IndexFlatL2
    assert faiss_mock.read_index.call_count == 0 # Shouldn't read if file doesn't exist
    assert faiss_mock.IndexFlatL2.call_count == 1 # Should create a new index

def test_index_documents(retriever):
    """Test that documents are indexed correctly."""
    embeddings = [np.array([0.1] * 768), np.array([0.2] * 768)]
    metadata = [{"id": "doc1"}, {"id": "doc2"}]

    retriever.index(embeddings, metadata)

    # Verify that faiss 'add' was called with the correct vectors
    assert mock_index_instance.add.call_count == 1
    # Verify metadata is stored
    assert len(retriever.metadata_store) == 2
    assert retriever.metadata_store[0]["id"] == "doc1"
    assert "_lineage" in retriever.metadata_store[0] # Check for governance tag
    # Verify the index is written to disk
    faiss_mock.write_index.assert_called_with(mock_index_instance, retriever.index_path)


def test_query_functionality(retriever, mock_embed_fn):
    """Test the query functionality of the retriever."""
    # First, index some data
    embeddings = [np.array([i * 0.1] * 768) for i in range(3)]
    metadata = [{"id": f"doc{i}"} for i in range(3)]
    retriever.index(embeddings, metadata)

    # Mock the search result from the faiss index
    # Let's say the query is closest to doc2 and doc0
    mock_index_instance.search.return_value = (
        np.array([[0.1, 0.5]]), # Distances
        np.array([[2, 0]])      # Indices (doc2, doc0)
    )

    query_text = "find me a document"
    results = retriever.query(query_text, top_k=2)

    # Verify the embedding function was called for the query
    mock_embed_fn.assert_called_with(query_text)
    # Verify faiss 'search' was called
    mock_index_instance.search.assert_called_once()

    # Check the results
    assert len(results) == 2
    assert results[0]["id"] == 2 # Corresponds to index 2
    assert results[0]["metadata"]["id"] == "doc2"
    assert results[1]["id"] == 0 # Corresponds to index 0
    assert results[1]["metadata"]["id"] == "doc0"
    assert "_lineage" in results[0]["metadata"]
