FROM python:3.13-slim as development
WORKDIR /app
# configure uv
RUN pip install --no-cache-dir uv
COPY server/pyproject.toml server/uv.lock ./
RUN uv sync
# copy src
COPY server/ .
# copy frontend build artifacts produced on host into image at /app/dist
COPY client/dist ./dist
# run server
CMD ["uv", "run", "fastapi", "dev", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.13-slim as production
WORKDIR /app
# configure uv
RUN pip install --no-cache-dir uv
COPY server/pyproject.toml server/uv.lock ./
RUN uv sync --no-dev
# copy src
COPY server/ .
# copy frontend build artifacts produced on host into image at /app/dist
COPY client/dist ./dist
# run server
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]