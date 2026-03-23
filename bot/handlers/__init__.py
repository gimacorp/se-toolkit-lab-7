"""Command handlers for the Telegram bot.

Handlers are pure functions that take input and return text responses.
They don't depend on Telegram - this enables --test mode for offline verification.
"""


async def handle_start() -> str:
    """Handle /start command.

    Returns:
        Welcome message for new users.
    """
    return (
        "👋 Welcome to the LMS Bot!\n\n"
        "I can help you check your lab progress and scores.\n\n"
        "Available commands:\n"
        "/help - Show this help message\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores [lab_id] - Get your scores"
    )


async def handle_help() -> str:
    """Handle /help command.

    Returns:
        List of available commands with descriptions.
    """
    return (
        "📚 LMS Bot Commands:\n\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores [lab_id] - Get scores for a lab\n\n"
        "You can also ask questions in natural language!"
    )


async def handle_health() -> str:
    """Handle /health command.

    Returns:
        Backend health status.
    """
    # Placeholder - will be implemented in Task 2
    return "🟡 Backend status: Not implemented yet (Task 2)"


async def handle_labs() -> str:
    """Handle /labs command.

    Returns:
        List of available labs.
    """
    # Placeholder - will be implemented in Task 2
    return "📋 Available labs: Not implemented yet (Task 2)"


async def handle_scores(lab_id: str | None = None) -> str:
    """Handle /scores command.

    Args:
        lab_id: Optional lab identifier to filter scores.

    Returns:
        User's scores information.
    """
    # Placeholder - will be implemented in Task 2
    if lab_id:
        return f"📊 Scores for {lab_id}: Not implemented yet (Task 2)"
    return "📊 Your scores: Not implemented yet (Task 2)"


async def handle_natural_language(query: str) -> str:
    """Handle natural language queries.

    Args:
        query: User's question in natural language.

    Returns:
        Response based on intent analysis.
    """
    # Placeholder - will be implemented in Task 3
    return f"🤔 You asked: '{query}'. Intent routing coming in Task 3!"
