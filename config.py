"""
Configuration management for Buddy AI.
All settings are centralized here and can be overridden via environment variables.
"""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """Application configuration with environment variable overrides."""

    # Paths
    APP_DIR: Path = Path(__file__).parent.resolve()
    DATA_PATH: Path = None
    DB_PATH: Path = None
    CHAT_HISTORY_FILE: Path = None

    # RAG Configuration
    CHUNK_SIZE: int = 1500
    CHUNK_OVERLAP: int = 300
    RETRIEVER_K: int = 6
    LLM_TEMPERATURE: float = 0.3
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    PINECONE_INDEX: str = "buddy-ai-index"

    # Rate Limiting
    RATE_LIMIT_MESSAGES: int = 30
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # Session
    SESSION_TIMEOUT_HOURS: int = 24

    # Input Validation
    MAX_INPUT_LENGTH: int = 2000

    # Memory System
    MEMORY_REFERENCE_INTERVAL: int = 5  # Reference memory every N messages

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def __post_init__(self):
        """Initialize paths and load environment overrides."""
        # Set up paths
        self.DATA_PATH = self.APP_DIR / "data"
        self.DB_PATH = self.DATA_PATH / "buddy_ai.db"
        self.CHAT_HISTORY_FILE = self.DATA_PATH / "chat_history.json"

        # Load environment variable overrides
        self._load_env_overrides()

    def _load_env_overrides(self):
        """Load configuration from environment variables."""
        # RAG
        self.CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", self.CHUNK_SIZE))
        self.CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", self.CHUNK_OVERLAP))
        self.RETRIEVER_K = int(os.getenv("RETRIEVER_K", self.RETRIEVER_K))
        self.LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", self.LLM_TEMPERATURE))
        self.LLM_MODEL = os.getenv("LLM_MODEL", self.LLM_MODEL)
        self.PINECONE_INDEX = os.getenv("PINECONE_INDEX", self.PINECONE_INDEX)

        # Rate Limiting
        self.RATE_LIMIT_MESSAGES = int(os.getenv("RATE_LIMIT_MESSAGES", self.RATE_LIMIT_MESSAGES))
        self.RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", self.RATE_LIMIT_WINDOW))

        # Session
        self.SESSION_TIMEOUT_HOURS = int(os.getenv("SESSION_TIMEOUT_HOURS", self.SESSION_TIMEOUT_HOURS))

        # Input
        self.MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", self.MAX_INPUT_LENGTH))

        # Memory
        self.MEMORY_REFERENCE_INTERVAL = int(os.getenv("MEMORY_REFERENCE_INTERVAL", self.MEMORY_REFERENCE_INTERVAL))

        # Logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", self.LOG_LEVEL)


@dataclass
class RequiredEnvVars:
    """Required environment variables for the application."""
    OPENAI_API_KEY: str = "OPENAI_API_KEY"
    PINECONE_API_KEY: str = "PINECONE_API_KEY"


def validate_environment() -> tuple[bool, list[str]]:
    """
    Validate that all required environment variables are set.

    Returns:
        Tuple of (is_valid, list of missing variables)
    """
    required = RequiredEnvVars()
    missing = []

    for var_name in [required.OPENAI_API_KEY, required.PINECONE_API_KEY]:
        if not os.getenv(var_name):
            missing.append(var_name)

    return len(missing) == 0, missing


def get_config() -> AppConfig:
    """Get the application configuration singleton."""
    if not hasattr(get_config, "_instance"):
        get_config._instance = AppConfig()
    return get_config._instance


def setup_logging(config: Optional[AppConfig] = None) -> None:
    """Configure logging based on config settings."""
    if config is None:
        config = get_config()

    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
        format=config.LOG_FORMAT
    )


# Environment validation on import (warns but doesn't fail)
def check_environment_on_import():
    """Check environment on module import and log warnings."""
    is_valid, missing = validate_environment()
    if not is_valid:
        logger.warning(f"Missing environment variables: {', '.join(missing)}")
        logger.warning("Some features may not work correctly.")


# Run check on import
check_environment_on_import()
