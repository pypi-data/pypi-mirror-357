FROM python:3.12-slim

ARG UV_INDEX_GEMFURY_USERNAME

ENV UV_INDEX_GEMFURY_USERNAME=${UV_INDEX_GEMFURY_USERNAME}

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
COPY pyproject.toml uv.lock ./

# Install dependencies globally
# RUN uv pip install --system -r pyproject.toml
RUN --mount=type=secret,id=gemfury-token,env=UV_INDEX_GEMFURY_PASSWORD \
    echo TOKEN: $UV_INDEX_GEMFURY_PASSWORD \
    uv pip install --system -r pyproject.toml