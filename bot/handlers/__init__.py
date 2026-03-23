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

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "handle_natural_language",
]
