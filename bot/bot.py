#!/usr/bin/env python3
"""Telegram bot entry point with --test mode support.

Usage:
    uv run bot.py              # Run in Telegram mode (requires BOT_TOKEN)
    uv run bot.py --test "/start"  # Run in test mode (no Telegram connection)
    uv run bot.py --test "what labs are available"  # Natural language query
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add bot directory to path for imports
bot_dir = Path(__file__).parent
sys.path.insert(0, str(bot_dir))

from config import is_test_mode, load_config
from handlers import (
    handle_help,
    handle_health,
    handle_labs,
    handle_natural_language,
    handle_scores,
    handle_start,
)


def parse_command(text: str) -> tuple[str, str | None]:
    """Parse a command string into command and argument.

    Args:
        text: User input text (e.g., "/scores lab-04" or "/start")

    Returns:
        Tuple of (command, argument). Argument is None if not provided.
    """
    parts = text.strip().split(maxsplit=1)
    command = parts[0].lower() if parts else ""
    argument = parts[1] if len(parts) > 1 else None
    return command, argument


async def run_command(command: str, argument: str | None = None, debug: bool = False) -> str:
    """Execute a command and return the response.

    Args:
        command: Command name (e.g., "/start", "/help")
        argument: Optional command argument
        debug: If True, enable debug output for natural language queries

    Returns:
        Response text from the handler.
    """
    if command == "/start":
        return await handle_start()
    elif command == "/help":
        return await handle_help()
    elif command == "/health":
        return await handle_health()
    elif command == "/labs":
        return await handle_labs()
    elif command == "/scores":
        return await handle_scores(argument)
    else:
        # Treat as natural language query
        full_text = f"{command} {argument}" if argument else command
        return await handle_natural_language(full_text, debug=debug)


async def run_test_mode(command_text: str, debug: bool = False) -> None:
    """Run a command in test mode and print result to stdout.

    Args:
        command_text: Full command text (e.g., "/start" or "/scores lab-04")
        debug: If True, enable debug output to stderr
    """
    command, argument = parse_command(command_text)
    
    # Check if it looks like a command or natural language
    if command.startswith("/"):
        response = await run_command(command, argument, debug=debug)
    else:
        # Natural language query - treat entire input as the query
        response = await handle_natural_language(command_text, debug=debug)
    
    print(response)


async def run_telegram_mode() -> None:
    """Run the bot in Telegram mode.

    This will be implemented in Task 4 when we add aiogram integration.
    """
    config = load_config()

    if not config.bot_token:
        print(
            "Error: BOT_TOKEN not set. Please create .env.bot.secret with your bot token.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Telegram bot implementation will be added in Task 4
    # For now, show a message that test mode is available
    print("Telegram bot mode - coming in Task 4!")
    print("Use --test mode for now: uv run bot.py --test 'what labs are available'")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LMS Telegram Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    uv run bot.py --test "/start"                  Test /start command
    uv run bot.py --test "/help"                   Test /help command
    uv run bot.py --test "/health"                 Test /health command
    uv run bot.py --test "/labs"                   Test /labs command
    uv run bot.py --test "/scores lab-04"          Test /scores with argument
    uv run bot.py --test "what labs are available" Natural language query
    uv run bot.py --test "which lab has lowest pass rate"  Multi-step query
        """,
    )
    parser.add_argument(
        "--test",
        metavar="QUERY",
        help="Run in test mode with the specified command or natural language query (no Telegram connection)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output (shows LLM tool calls to stderr)",
    )

    args = parser.parse_args()

    if args.test:
        # Test mode - run command and print result
        asyncio.run(run_test_mode(args.test, debug=args.debug))
    else:
        # Telegram mode - run the actual bot
        asyncio.run(run_telegram_mode())


if __name__ == "__main__":
    main()
