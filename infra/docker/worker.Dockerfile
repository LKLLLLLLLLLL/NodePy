# file structure of the container
# /nodepy/
#   ├── pyproject.toml
#   ├── uv.lock
#   ├── server/          # backend (-> project-root/server/)
#   │   ├── app/
#   │   │   └── main.py
#   │   └── ...
#   └── static/          # frontend static files (-> project-root/client/dist/)
#       ├── index.html
#       ├── assets/
#       └── ...

FROM python:3.13 AS development
WORKDIR /nodepy
# install fonts for visualizations
RUN apt-get upgrade && apt-get update && apt-get install -y \
    fonts-noto-cjk \
    fonts-roboto \
    && rm -rf /var/lib/apt/lists/*
# configure uv
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-group server --no-group dev --group worker
# copy src (in dev mode, this will be overridden by volume mount)
# COPY server /nodepy/server
# copy frontend build artifacts (in dev mode, /nodepy/static will be mounted)
# COPY client/dist /nodepy/static
# run server
CMD ["uv", "run", "celery", "-A", "server.celery", "worker", "--beat", "--loglevel=debug"]

FROM python:3.13 AS production
WORKDIR /nodepy
# install fonts for visualizations
RUN apt-get upgrade && apt-get update && apt-get install -y \
    fonts-noto-cjk \
    fonts-roboto \
    && rm -rf /var/lib/apt/lists/*
# configure uv
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-group server --no-group dev --group worker
# copy src
COPY server /nodepy/server
# copy frontend build artifacts produced on host into image
COPY client/dist /nodepy/static
# run server
CMD ["uv", "run", "celery", "-A", "server.celery", "worker", "--beat", "--loglevel=info"]
