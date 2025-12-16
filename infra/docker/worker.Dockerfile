# file structure of the container
# /nodepy/
#   ├── pyproject.toml
#   ├── uv.lock
#   ├── server/          # backend (-> project-root/server/)
#   │   ├── app/
#   │   │   └── main.py
#   │   └── ...
#   ├── static/          # frontend static files (-> project-root/client/dist/)
#   │   ├── index.html
#   │   ├── assets/
#   │   └── ...
#   └── scripts/         # utility scripts
#       └── ...

FROM python:3.13 AS development
WORKDIR /nodepy
# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot
# Install fonts for visualizations
RUN apt-get upgrade && apt-get update && apt-get install -y \
    fonts-noto-cjk \
    fonts-roboto \
    && rm -rf /var/lib/apt/lists/*
# Configure uv
RUN pip install --no-cache-dir uv
# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy
# Omit development dependencies
ENV UV_NO_DEV=1
COPY pyproject.toml uv.lock ./
RUN uv sync --no-install-project --no-group server --no-group dev --group worker
# No need to copy src (in dev mode, this will be overridden by volume mount)
# Use the non-root user to run our application
USER nonroot
# Run server
CMD ["uv", "run", "celery", "-A", "server.celery", "worker", "--beat", "--schedule", "/tmp/celerybeat-schedule", "--loglevel=debug"]


FROM python:3.13 AS production
WORKDIR /nodepy
# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot
# Install fonts for visualizations
RUN apt-get upgrade && apt-get update && apt-get install -y \
    fonts-noto-cjk \
    fonts-roboto \
    && rm -rf /var/lib/apt/lists/*
# Configure uv
RUN pip install --no-cache-dir uv
# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy
# Omit development dependencies
ENV UV_NO_DEV=1
COPY pyproject.toml uv.lock ./
RUN uv sync --no-install-project --no-group server --no-group dev --group worker
# Copy src
COPY server /nodepy/server
# Copy frontend build artifacts produced on host into image
COPY client/dist /nodepy/static
# Copy scripts
COPY scripts /nodepy/scripts
# Use the non-root user to run our application
USER nonroot
# Run server
CMD ["uv", "run", "celery", "-A", "server.celery", "worker", "--beat", "--schedule", "/tmp/celerybeat-schedule", "--loglevel=info"]
