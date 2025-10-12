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


FROM python:3.13-slim as development
WORKDIR /nodepy
# configure uv
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync
# copy src (in dev mode, this will be overridden by volume mount)
# COPY server /nodepy/server
# copy frontend build artifacts (in dev mode, /nodepy/static will be mounted)
# COPY client/dist /nodepy/static
# run server
CMD ["uv", "run", "fastapi", "dev", "server/app/main.py", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.13-slim as production
WORKDIR /nodepy
# configure uv
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev
# copy src
COPY server /nodepy/server
# copy frontend build artifacts produced on host into image
COPY client/dist /nodepy/static
# run server
CMD ["uv", "run", "uvicorn", "server.app.main:app", "--host", "0.0.0.0", "--port", "8000"]