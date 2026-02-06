"""
Pytest configuration and fixtures for Buddy AI tests.
"""
import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_db():
    """Create a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        yield f.name
    # Cleanup
    try:
        os.unlink(f.name)
    except OSError:
        pass


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_messages():
    """Sample chat messages for testing."""
    return [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there! How can I help you today?"},
        {"role": "user", "content": "I want to know about engineering careers"},
        {"role": "assistant", "content": "Engineering is a great field! What aspects interest you?"},
    ]


@pytest.fixture
def sample_student_profile():
    """Sample student profile data for testing."""
    return {
        "interests": ["technology", "problem solving"],
        "dislikes": ["memorization"],
        "strengths": ["math", "logical thinking"],
        "challenges": ["public speaking"],
        "careers_discussed": [
            {"career": "software engineer", "sentiment": "positive"},
            {"career": "data scientist", "sentiment": "curious"},
        ]
    }


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-12345")
    monkeypatch.setenv("PINECONE_API_KEY", "test-pinecone-key")
    yield


@pytest.fixture
def conversation_states():
    """All conversation states for testing."""
    from conversation.constants import ConversationState
    return ConversationState
