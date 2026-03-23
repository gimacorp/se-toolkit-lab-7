"""Command handlers for the Telegram bot.

Handlers are pure functions that take input and return text responses.
They don't depend on Telegram - this enables --test mode for offline verification.
"""

import httpx

from config import load_config
from handlers.intent_router import route_natural_language
from services.lms_client import LMSClient


def _get_lms_client() -> LMSClient:
    """Create an LMS client from configuration.
    
    Returns:
        Configured LMSClient instance.
        
    Raises:
        ValueError: If LMS API configuration is missing.
    """
    config = load_config()
    if not config.lms_api_base_url:
        raise ValueError("LMS_API_BASE_URL not configured")
    if not config.lms_api_key:
        raise ValueError("LMS_API_KEY not configured")
    return LMSClient(
        base_url=config.lms_api_base_url,
        api_key=config.lms_api_key,
        timeout=5.0,
    )


async def handle_start() -> str:
    """Handle /start command.

    Returns:
        Welcome message for new users.
    """
    config = load_config()
    bot_name = "LMS Bot"
    if config.bot_token:
        # Extract bot name from token if available (optional)
        pass
    
    return (
        f"👋 Welcome to {bot_name}!\n\n"
        "I can help you check your lab progress and scores.\n\n"
        "Available commands:\n"
        "/help - Show this help message\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores [lab_id] - Get your scores\n\n"
        "Or just ask me questions like:\n"
        "• \"Which lab has the lowest pass rate?\"\n"
        "• \"Show me scores for lab 4\"\n"
        "• \"Who are the top 5 students?\""
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
        "You can also ask questions in natural language!\n"
        "Examples:\n"
        "• \"what labs are available?\"\n"
        "• \"which lab has the lowest pass rate?\"\n"
        "• \"show me scores for lab 4\"\n"
        "• \"who are the top 5 students in lab 4\""
    )


async def handle_health() -> str:
    """Handle /health command.

    Returns:
        Backend health status with item count or error message.
    """
    try:
        client = _get_lms_client()
        result = await client.health_check()
        return f"🟢 Backend is healthy. {result['item_count']} items available."
    except httpx.ConnectError as e:
        return f"🔴 Backend error: connection refused ({e.request.url.host}:{e.request.url.port}). Check that the services are running."
    except httpx.TimeoutException as e:
        return f"🔴 Backend error: request timed out. The service may be overloaded."
    except httpx.HTTPStatusError as e:
        return f"🔴 Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except httpx.RequestError as e:
        return f"🔴 Backend error: {str(e)}. Check your network connection."
    except ValueError as e:
        return f"🔴 Configuration error: {e}"


async def handle_labs() -> str:
    """Handle /labs command.

    Returns:
        List of available labs formatted for display.
    """
    try:
        client = _get_lms_client()
        items = await client.get_items()
        
        if not items:
            return "📋 No labs available. The backend may not have synced data yet."
        
        # Group items by lab (items with same lab_id)
        labs = {}
        for item in items:
            lab_id = item.get("lab_id", "unknown")
            lab_name = item.get("lab_name", "Unknown Lab")
            if lab_id not in labs:
                labs[lab_id] = lab_name
        
        if not labs:
            return "📋 No labs found in the backend."
        
        lines = ["📋 Available labs:"]
        for lab_id, lab_name in sorted(labs.items()):
            lines.append(f"- {lab_name}")
        
        return "\n".join(lines)
        
    except httpx.ConnectError:
        return f"🔴 Backend error: connection refused. Check that the services are running."
    except httpx.TimeoutException:
        return f"🔴 Backend error: request timed out. The service may be overloaded."
    except httpx.HTTPStatusError as e:
        return f"🔴 Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}."
    except httpx.RequestError as e:
        return f"🔴 Backend error: {str(e)}."
    except ValueError as e:
        return f"🔴 Configuration error: {e}"


async def handle_scores(lab_id: str | None = None) -> str:
    """Handle /scores command.

    Args:
        lab_id: Optional lab identifier to filter scores.

    Returns:
        User's scores information formatted for display.
    """
    if not lab_id:
        return "📊 Usage: /scores <lab_id>\n\nExample: /scores lab-04\n\nUse /labs to see available labs."
    
    try:
        client = _get_lms_client()
        pass_rates = await client.get_pass_rates(lab_id)
        
        if not pass_rates:
            return f"📊 No scores found for {lab_id}. The lab may not exist or has no submissions yet."
        
        lines = [f"📊 Pass rates for {lab_id}:"]
        for task in pass_rates:
            task_name = task.get("task_name", "Unknown Task")
            pass_rate = task.get("pass_rate", 0)
            attempts = task.get("attempts", 0)
            lines.append(f"- {task_name}: {pass_rate:.1f}% ({attempts} attempts)")
        
        return "\n".join(lines)
        
    except httpx.ConnectError:
        return f"🔴 Backend error: connection refused. Check that the services are running."
    except httpx.TimeoutException:
        return f"🔴 Backend error: request timed out. The service may be overloaded."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"📊 Lab '{lab_id}' not found. Use /labs to see available labs."
        return f"🔴 Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}."
    except httpx.RequestError as e:
        return f"🔴 Backend error: {str(e)}."
    except ValueError as e:
        return f"🔴 Configuration error: {e}"


async def handle_natural_language(query: str, debug: bool = False) -> str:
    """Handle natural language queries using LLM intent routing.

    Args:
        query: User's question in natural language.
        debug: If True, print debug info to stderr.

    Returns:
        Response based on intent analysis and API data.
    """
    # Check for greetings and simple cases without LLM
    query_lower = query.strip().lower()
    
    # Greeting fallback
    if query_lower in ["hello", "hi", "hey", "привет", "здравствуйте"]:
        return "👋 Hello! I'm the LMS Bot. Ask me about labs, scores, or student performance. For example: \"Which lab has the lowest pass rate?\""
    
    # Gibberish detection (very short or no letters)
    if len(query_lower) < 3 or not any(c.isalpha() for c in query_lower):
        return (
            "🤔 I didn't understand that. Here's what I can help with:\n\n"
            "• \"what labs are available?\"\n"
            "• \"which lab has the lowest pass rate?\"\n"
            "• \"show me scores for lab 4\"\n"
            "• \"who are the top 5 students?\"\n"
            "• \"compare group performance\""
        )
    
    # Use LLM for intent routing
    return await route_natural_language(query, debug=debug)
