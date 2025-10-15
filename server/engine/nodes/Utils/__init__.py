"""Package initializer for `server.engine.nodes.Utils`.

This module re-exports `GlobalConfig` by dynamically loading the sibling
module file `../Utils.py` (the top-level Utils module) to avoid importing
the nested `Utils/Utils.py` which depends on `BaseNode` and would create a
circular import during test collection.
"""

from pathlib import Path
import importlib.util

# locate the top-level Utils.py (one directory above this package)
_top_utils = Path(__file__).resolve().parent.parent / "Utils.py"
spec = importlib.util.spec_from_file_location("server.engine.nodes._utils_top", str(_top_utils))
_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_mod)

# export GlobalConfig
GlobalConfig = getattr(_mod, "GlobalConfig")

__all__ = ["GlobalConfig"]
