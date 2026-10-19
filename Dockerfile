FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Copy dependency files first so this layer caches across code changes
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project

# Copy the project code
COPY lib/ lib/
COPY data/ data/

# Download the ML model during the build so the container works offline
RUN uv run --no-sync python -c "from lib.model import phishing_model; phishing_model.download_model()"

EXPOSE 8080

# Run the proxy addon through mitmdump
CMD ["uv", "run", "--no-sync", "mitmdump", "--listen-port", "8080", "-s", "lib/proxy_addon.py"]
