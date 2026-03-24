"""Command handlers for the Telegram bot.

Handlers are pure functions that take input and return text responses.
They don't depend on Telegram - this enables --test mode for offline verification.
"""

from handlers.commands import (
    handle_help,
    handle_health,
    handle_labs,
    handle_natural_language,
    handle_scores,
    handle_start,
)
from handlers.keyboards import (
    get_back_keyboard,
    get_help_keyboard,
    get_lab_actions_keyboard,
    get_start_keyboard,
)

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "handle_natural_language",
    "get_start_keyboard",
    "get_help_keyboard",
    "get_lab_actions_keyboard",
    "get_back_keyboard",
]
