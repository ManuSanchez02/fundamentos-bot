FROM ghcr.io/astral-sh/uv:alpine

# Install dependencies
COPY src pyproject.toml README.md uv.lock /app/
WORKDIR /app
RUN uv sync --frozen

# Run the bot
CMD ["uv", "run", "bot"]
