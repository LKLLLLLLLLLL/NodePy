import os
import sys

from loguru import logger

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# config logging system
LEVEL = "DEBUG" if DEBUG else "INFO"

logger.remove()  # remove default handler
logger.add(
    sys.stdout,
    level=LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss,ms}: [{level}] <{function}> {message}",
)
try:
    logger.add(
        "/nodepy/logs/server.log",
        rotation="10 MB",
        level=LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss,ms}: [{level}] <{function}> {message}",
    )
except Exception:
    # Could be OSError on read-only filesystem or other issues creating dirs.
    logger.warning("Cannot write log file to /nodepy/logs/server.log; continuing without file sink.")
