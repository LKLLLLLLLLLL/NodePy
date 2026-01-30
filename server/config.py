import os
from datetime import timezone
from pathlib import Path
from string import ascii_letters, digits, punctuation

"""
This file set some global configurations for the NodePy.
"""


"""
Deployment and environment settings
"""

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Minio configuration
MINIO_URL = str(os.getenv("MINIO_ENDPOINT", ""))
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "")
MINIO_SECURE = False  # MinIO in Docker is HTTP, not HTTPS

# Authentication configuration
AUTH_SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
AUTH_ALGORITHM = "HS256"
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES = 30
AUTH_REFRESH_TOKEN_EXPIRE_DAYS = 7

# Celery configuration
CELERY_REDIS_URL = REDIS_URL + "/0"

# Stream Queue configuration
STREAMQUEUE_REDIS_URL = REDIS_URL + "/1"
STREAMQUEUE_TTL_SECONDS = 3600  # 1 hour

# Cache configuration
CACHE_REDIS_URL = REDIS_URL + "/2"
CACHE_TTL_SECONDS = 24 * 60 * 60  # 24 hour

# Project lock configuration
PROJ_LOCK_REDIS_URL = REDIS_URL + "/3"
PROJ_LOCK_RETRY_INTERVAL = 0.1  # seconds
PROJ_LOCK_APPOINTED_LOCK_EXPIRY = 30  # seconds


"""
Business logic settings
"""

# The fallback timezone if user provided none
# DEFAULT_TIMEZONE = timezone(timedelta(hours=8)) # UTC+8 
DEFAULT_TIMEZONE = timezone.utc  # UTC+0

FIGURE_DPI = 500  # Default DPI for matplotlib figures

# The default core symbols to be tracked by the FinancialDataManager
CORE_SYMBOLS = {
    "crypto": ["BTCUSDT", "ETHUSDT"],
    "stock": ["AAPL", "GOOGL", "TSLA"],
}

# Example projects configuration
EXAMPLE_USER_USERNAME = "NodePy-Learning"
EXAMPLE_USER_EMAIL = "learning@nodepy.com"
EXAMPLES_DIR = Path("/nodepy/server/assets/examples")

# Interpreter configuration
TASK_MAX_RUNNING_TIME_SEC = 30 * 60  # 30 minutes
CUSTOM_SCRIPT_MAX_TIME_SEC = 5  # 5 seconds

# Fetch financial data configuration
FETCH_FORWARD_INTERVAL_SEC = 5 * 60.0  # 5 minutes
FETCH_BACKWARD_INTERVAL_SEC = 10 * 60.0  # 10 minutes

# User storage configuration
USER_DEFAULT_STORAGE_MB = 5 * 1024  # 5 GB

# Cleanup configuration
CLEAN_ORPHAN_FILE_INTERVAL_SEC = 60 * 60.0  # 1 hour

# Username and password requirements
USERNAME_MIN_LENGTH = 1
USERNAME_MAX_LENGTH = 20
USERNAME_ALLOWED_CHARS = set(ascii_letters + digits + punctuation)
USERNAME_ALLOWED_UTF8 = True  # Whether to allow UTF characters in username
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 20
PASSWORD_ALLOWED_CHARS = set(ascii_letters + digits + punctuation)

# Limitations for generated tables
MAX_GENERATED_TABLE_ROWS = 1000000  # Maximum rows allowed for generated tables

"""
Debugging and logging settings
"""

# Whether to use caching mechanism globally
USE_CACHE = True

# Whether to enable time tracing for interpreter
TRACING_ENABLED = True
