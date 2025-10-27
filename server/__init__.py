from loguru import logger
import sys
import os

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# config logging system
LEVEL = "DEBUG" if DEBUG else "INFO"

logger.remove()  # remove default handler
logger.add(
    sys.stdout,
    level=LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss,ms}: [{level}] <{function}> {message}",
)
logger.add(
    "/nodepy/logs/server.log",
    rotation="10 MB",
    level=LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss,ms}: [{level}] <{function}> {message}",
)
