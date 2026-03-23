"""Configuration loading from environment variables."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    # Telegram
    bot_token: str = ""

    # LMS API
    lms_api_base_url: str = ""
    lms_api_key: str = ""

    # LLM API
    llm_api_model: str = "coder-model"
    llm_api_key: str = ""
    llm_api_base_url: str = ""

    class Config:
        env_file = ".env.bot.secret"
        env_file_encoding = "utf-8"


def load_config() -> BotSettings:
    """Load configuration from .env.bot.secret file.

    The file should be in the same directory as this config module.
    """
    # Find the directory where this config file is located
    bot_dir = Path(__file__).parent
    env_file = bot_dir / ".env.bot.secret"

    if not env_file.exists():
        # Fall back to environment variables only
        return BotSettings()

    return BotSettings(env_file=str(env_file))


def is_test_mode() -> bool:
    """Check if running in test mode (no Telegram connection)."""
    return os.environ.get("BOT_TEST_MODE", "false").lower() == "true"
