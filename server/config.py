from datetime import timezone
from pathlib import Path

"""
This file set some global configurations for the NodePy.
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

# Whether to use caching mechanism globally
USE_CACHE = True

# Whether to enable time tracing for interpreter
TRACING_ENABLED = True

# Configure example projects
EXAMPLE_USER_USERNAME = "NodePy-Learning"
EXAMPLE_USER_EMAIL = "learning@nodepy.com"
EXAMPLES_DIR = Path("/nodepy/server/assets/examples")
