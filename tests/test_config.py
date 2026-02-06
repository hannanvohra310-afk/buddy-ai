"""
Tests for configuration management.
"""
import pytest
import os


class TestAppConfig:
    """Tests for AppConfig class."""

    def test_default_values(self):
        """Test that default configuration values are set correctly."""
        from config import AppConfig

        config = AppConfig()

        assert config.CHUNK_SIZE == 1500
        assert config.CHUNK_OVERLAP == 300
        assert config.RETRIEVER_K == 6
        assert config.LLM_TEMPERATURE == 0.3
        assert config.RATE_LIMIT_MESSAGES == 30
        assert config.RATE_LIMIT_WINDOW == 60
        assert config.SESSION_TIMEOUT_HOURS == 24
        assert config.MAX_INPUT_LENGTH == 2000

    def test_paths_initialized(self):
        """Test that paths are properly initialized."""
        from config import AppConfig

        config = AppConfig()

        assert config.DATA_PATH is not None
        assert config.DB_PATH is not None
        assert config.CHAT_HISTORY_FILE is not None
        assert str(config.DB_PATH).endswith("buddy_ai.db")
        assert str(config.CHAT_HISTORY_FILE).endswith("chat_history.json")

    def test_env_override(self, monkeypatch):
        """Test that environment variables override defaults."""
        monkeypatch.setenv("CHUNK_SIZE", "2000")
        monkeypatch.setenv("RATE_LIMIT_MESSAGES", "50")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        from config import AppConfig

        config = AppConfig()

        assert config.CHUNK_SIZE == 2000
        assert config.RATE_LIMIT_MESSAGES == 50
        assert config.LOG_LEVEL == "DEBUG"


class TestEnvironmentValidation:
    """Tests for environment validation."""

    def test_missing_env_vars(self, monkeypatch):
        """Test detection of missing environment variables."""
        # Clear the env vars
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("PINECONE_API_KEY", raising=False)

        from config import validate_environment

        is_valid, missing = validate_environment()

        assert is_valid is False
        assert "OPENAI_API_KEY" in missing
        assert "PINECONE_API_KEY" in missing

    def test_valid_env_vars(self, mock_env_vars):
        """Test validation passes with all env vars set."""
        from config import validate_environment

        is_valid, missing = validate_environment()

        assert is_valid is True
        assert len(missing) == 0


class TestGetConfig:
    """Tests for get_config singleton."""

    def test_singleton_pattern(self):
        """Test that get_config returns the same instance."""
        from config import get_config

        config1 = get_config()
        config2 = get_config()

        assert config1 is config2
