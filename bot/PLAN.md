# Bot Development Plan

## Overview

This document describes the approach for building a Telegram bot that integrates with the Learning Management System (LMS) backend. The bot provides students with quick access to their lab progress, scores, and course information through natural language commands.

## Architecture

The bot follows a **layered architecture** with clear separation of concerns:

1. **Transport Layer** (`bot.py`) — Handles Telegram Bot API communication using aiogram. This layer is responsible for receiving updates from Telegram and sending responses back.

2. **Handler Layer** (`handlers/`) — Contains command handlers that process user input and return responses. Handlers are **testable functions** that don't depend on Telegram — they take input and return text. This enables the `--test` mode for offline verification.

3. **Service Layer** (`services/`) — External API clients:
   - `lms_client.py` — HTTP client for the LMS backend API with Bearer token authentication
   - `llm_client.py` — LLM client for intent routing (Task 3)

4. **Configuration** (`config.py`) — Loads environment variables from `.env.bot.secret` for secrets management.

## Task 1: Project Scaffold

Create the basic project structure with placeholder handlers. Implement `--test` mode that calls handlers directly without Telegram connectivity. This enables rapid development and testing without deploying to Telegram.

**Key decision:** Handlers return plain text, not Telegram messages. The bot entry point wraps handler responses for Telegram delivery.

## Task 2: Backend Integration

Implement real handlers that query the LMS backend:
- `/health` — Check backend availability and database connection
- `/labs` — List available labs and their status
- `/scores [lab_id]` — Get scores for a specific lab or all labs

The service layer handles HTTP requests, error handling, and response parsing. Handlers format responses for Telegram.

## Task 3: Intent-Based Routing

Add LLM-powered natural language understanding. Instead of requiring exact `/command` syntax, the bot understands questions like "what labs are available?" or "show my scores for lab 4".

**Approach:** Use the LLM to classify user intent and select the appropriate handler. Tool descriptions guide the LLM's decision-making. This is more flexible than regex-based routing and handles varied user phrasing.

## Task 4: Deployment

Containerize the bot and deploy to the university VM alongside the backend. Configure systemd or supervisor for process management. Set up logging and monitoring.

**Security:** Never commit `.env.bot.secret` — it's gitignored. Bot token and API keys are VM-only secrets.

## Testing Strategy

1. **Unit tests** — Test handlers in isolation with mocked services
2. **Test mode** — Manual verification via `--test` flag before each commit
3. **Integration tests** — Verify bot responds correctly in Telegram after deployment

## Development Workflow

1. Create feature branch from `main`
2. Implement changes with `--test` verification
3. Commit with descriptive message
4. Create PR, request partner review
5. Merge after approval
6. Pull on VM and restart bot
