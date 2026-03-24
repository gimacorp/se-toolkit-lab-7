# Build stage
FROM python:3.14.2-slim AS builder

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy bot files
COPY bot/pyproject.toml bot/uv.lock ./

# Sync dependencies
RUN uv sync --frozen

# Runtime stage
FROM python:3.14.2-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy synced environment from builder
COPY --from=builder /app/.venv /app/.venv
COPY bot/ /app/

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Run the bot
CMD ["python", "bot.py"]
