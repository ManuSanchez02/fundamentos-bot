from dotenv import load_dotenv
import os
from dataclasses import dataclass
import logging


@dataclass
class Config:
    """Configuration class for the bot."""

    token: str
    spreadsheet_id: str
    log_level: str | int = logging.INFO


def _getenv_or_raise(key: str) -> str:
    """Get an environment variable or raise an error if not found."""
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Environment variable {key} not found.")
    return value


def load_config() -> Config:
    """Load configuration from .env file."""
    load_dotenv()

    token = _getenv_or_raise("DISCORD_TOKEN")
    log_level = os.getenv("LOG_LEVEL", logging.INFO)
    spreadsheet_id = _getenv_or_raise("SPREADSHEET_ID")

    config = Config(
        token=token,
        log_level=log_level,
        spreadsheet_id=spreadsheet_id,
    )

    return config
