"""Configuration module to load environment variables for the bot."""

from dotenv import load_dotenv
import os
from dataclasses import dataclass
import logging


@dataclass
class Config:
    """Configuration class for the bot.

    Attributes:
        token: The Discord bot token.
        spreadsheet_id: The ID of the Google Spreadsheet.
        guild_id: The ID of the Discord guild.
        log_level: The logging level.
    """

    token: str
    spreadsheet_id: str
    guild_id: str | None = None
    log_level: str | int = logging.INFO


def _getenv_or_raise(key: str) -> str:
    """Get an environment variable or raise an error if not found.

    Args:
        key: The name of the environment variable.

    Returns:
        value: The value of the environment variable.

    Raises:
        ValueError: If the environment variable is not found.
    """
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Environment variable {key} not found.")
    return value


def load_config() -> Config:
    """Load configuration from the .env file.

    Returns:
        Config: Configuration object with the loaded values.

    Raises:
        ValueError: If required environment variables are not found.
    """
    load_dotenv()

    token = _getenv_or_raise("DISCORD_TOKEN")
    spreadsheet_id = _getenv_or_raise("SPREADSHEET_ID")
    log_level = os.getenv("LOG_LEVEL", logging.INFO)
    guild_id = os.getenv("DISCORD_GUILD_ID")

    config = Config(
        token=token,
        spreadsheet_id=spreadsheet_id,
        guild_id=guild_id,
        log_level=log_level,
    )

    return config
