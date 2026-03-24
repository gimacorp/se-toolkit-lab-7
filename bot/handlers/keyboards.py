"""Inline keyboard definitions for the Telegram bot.

This module provides keyboard layouts for common bot interactions.
Keyboards are returned as data structures that can be passed to aiogram.
"""

from typing import Any


def get_start_keyboard() -> list[list[dict[str, Any]]]:
    """Create inline keyboard for /start command.

    Returns:
        Inline keyboard markup with common query buttons.
    """
    return [
        [
            {
                "text": "📋 What labs are available?",
                "callback_data": "query_what_labs",
            },
        ],
        [
            {
                "text": "📊 Lowest pass rate",
                "callback_data": "query_lowest_pass_rate",
            },
            {
                "text": "🏆 Top students",
                "callback_data": "query_top_students",
            },
        ],
        [
            {
                "text": "📈 Scores for lab",
                "callback_data": "query_scores",
            },
            {
                "text": "👥 Group comparison",
                "callback_data": "query_groups",
            },
        ],
    ]


def get_help_keyboard() -> list[list[dict[str, Any]]]:
    """Create inline keyboard for /help command.

    Returns:
        Inline keyboard markup with help topic buttons.
    """
    return [
        [
            {
                "text": "📋 Available labs",
                "callback_data": "help_labs",
            },
            {
                "text": "📊 Analytics",
                "callback_data": "help_analytics",
            },
        ],
        [
            {
                "text": "🎓 Students",
                "callback_data": "help_students",
            },
            {
                "text": "❓ Examples",
                "callback_data": "help_examples",
            },
        ],
    ]


def get_lab_actions_keyboard(lab_id: str) -> list[list[dict[str, Any]]]:
    """Create inline keyboard for lab-specific actions.

    Args:
        lab_id: The lab identifier (e.g., "lab-04")

    Returns:
        Inline keyboard markup with lab action buttons.
    """
    return [
        [
            {
                "text": "📊 Pass rates",
                "callback_data": f"lab_{lab_id}_pass_rates",
            },
            {
                "text": "📈 Scores",
                "callback_data": f"lab_{lab_id}_scores",
            },
        ],
        [
            {
                "text": "👥 Groups",
                "callback_data": f"lab_{lab_id}_groups",
            },
            {
                "text": "🏆 Top learners",
                "callback_data": f"lab_{lab_id}_top",
            },
        ],
        [
            {
                "text": "📅 Timeline",
                "callback_data": f"lab_{lab_id}_timeline",
            },
            {
                "text": "✅ Completion rate",
                "callback_data": f"lab_{lab_id}_completion",
            },
        ],
    ]


def get_back_keyboard() -> list[list[dict[str, Any]]]:
    """Create a simple back button keyboard.

    Returns:
        Inline keyboard with just a back button.
    """
    return [
        [
            {
                "text": "« Back to menu",
                "callback_data": "back_menu",
            },
        ],
    ]
