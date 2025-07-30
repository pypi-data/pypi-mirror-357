FROM nvidia/cuda:12.8.0-devel-ubuntu22.04

ARG UV_INDEX_GEMFURY_USERNAME

ENV UV_INDEX_GEMFURY_USERNAME=${UV_INDEX_GEMFURY_USERNAME}

# Install curl
RUN apt-get update && apt-get install -y curl

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
COPY pyproject.toml ./

RUN --mount=type=secret,id=gemfury-token,env=UV_INDEX_GEMFURY_PASSWORD \
    echo TOKEN: $UV_INDEX_GEMFURY_PASSWORD \
    uv pip install --system -r pyproject.toml
