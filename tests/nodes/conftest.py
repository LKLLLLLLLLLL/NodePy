import atexit
import importlib
import shutil
import sys
import tempfile
import types
from pathlib import Path
from typing import Any, Generator

import pytest

# Ensure project root is on sys.path so `import server` works during pytest collection
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


# --- Create lightweight fake modules to avoid Docker/minio/redis/db imports at test-import time ---
_TEST_FILE_ROOT = tempfile.mkdtemp(prefix="nodepy_test_files_", dir=str(_PROJECT_ROOT))


def _cleanup_test_root() -> None:
    shutil.rmtree(_TEST_FILE_ROOT, ignore_errors=True)


atexit.register(_cleanup_test_root)


def _ensure_pkg(name: str) -> None:
    """Ensure a package module exists in sys.modules with a __path__ so
    importlib can treat it as a package. This reduces IDE/lint warnings.
    """
    if name in sys.modules:
        return
    mod = types.ModuleType(name)
    try:
        pkg_path = str(_PROJECT_ROOT / "server" / "lib")
        mod.__path__ = [pkg_path]
    except Exception:
        pass
    sys.modules[name] = mod  # type: ignore


_ensure_pkg("server.lib")


def _install_fake_modules() -> None:
    """Inject fake modules immediately so imports during collection use them."""

    # Fake FileManager
    fm_mod: Any = types.ModuleType("server.lib.FileManager")

    class _FakeFileManager:
        def __init__(self, *args, **kwargs):
            self.root = _TEST_FILE_ROOT

        def read_sync(self, file, user_id=None):
            import os

            from server.models.file import File

            if isinstance(file, File):
                path = os.path.join(self.root, file.key)
                try:
                    with open(path, "rb") as f:
                        return f.read()
                except Exception:
                    return b""
            return b""

        def write_sync(self, filename, content, format, node_id, project_id, user_id):
            import os

            from server.models.file import File

            key = f"{node_id}_{filename}"
            path = os.path.join(self.root, key)
            if hasattr(content, "read"):
                content = content.read()
            with open(path, "wb") as f:
                f.write(content)
            return File(key=key, filename=filename, format=format, size=len(content))

        def get_buffer(self):
            import io

            return io.BytesIO()

    fm_mod.FileManager = _FakeFileManager  # type: ignore[attr-defined]
    sys.modules["server.lib.FileManager"] = fm_mod

    # Fake FinancialDataManager with expected type aliases
    fdm_mod: Any = types.ModuleType("server.lib.FinancialDataManager")
    from typing import Literal as _Literal

    class _FakeFinancialDataManager:
        def __init__(self, *args, **kwargs):
            pass

        def get_kline(self, *args, **kwargs):
            import pandas as pd

            return pd.DataFrame()

    fdm_mod.DataType = _Literal["crypto", "stock"]  # type: ignore[attr-defined]
    fdm_mod.Interval = _Literal["1m", "1h", "1d"]  # type: ignore[attr-defined]
    fdm_mod.FinancialDataManager = _FakeFinancialDataManager  # type: ignore[attr-defined]
    sys.modules["server.lib.FinancialDataManager"] = fdm_mod

    # Fake CacheManager
    cm_mod: Any = types.ModuleType("server.lib.CacheManager")

    class _FakeCacheManager:
        def __init__(self, *args, **kwargs):
            pass

        def get(self, *args, **kwargs):
            return None

        def set(self, *args, **kwargs):
            return None

    cm_mod.CacheManager = _FakeCacheManager  # type: ignore[attr-defined]
    sys.modules["server.lib.CacheManager"] = cm_mod

    # Ensure server.lib.utils is available; prefer real implementation when present
    try:
        utils_real = importlib.import_module("server.lib.utils")
        sys.modules["server.lib.utils"] = utils_real  # type: ignore
    except Exception:
        utils_mod: Any = types.ModuleType("server.lib.utils")

        def _noop_safe_hash(obj):
            return ""

        def _noop_time_check(seconds, callback):
            def _decorator(f):
                return f

            return _decorator

        utils_mod.safe_hash = _noop_safe_hash  # type: ignore[attr-defined]
        utils_mod.time_check = _noop_time_check  # type: ignore[attr-defined]
        utils_mod.timeout = lambda s: (lambda f: f)  # type: ignore[attr-defined]
        sys.modules["server.lib.utils"] = utils_mod

_install_fake_modules()


@pytest.fixture(scope="session")
def test_file_root() -> Generator[str, None, None]:
    """Return the temp directory shared with fake managers for tests that need it."""

    yield _TEST_FILE_ROOT


@pytest.fixture(scope="session")
def node_registry() -> dict:
    """Return the node registry mapping type_name -> class.

    Import of `server.interpreter.nodes` is delayed until after fake modules are
    injected to avoid import-time errors.
    """
    from server.interpreter.nodes.base_node import _NODE_REGISTRY
    return _NODE_REGISTRY.copy()


@pytest.fixture
def global_config():
    """Return a GlobalConfig instance populated with fake managers."""
    from server.interpreter.nodes.config import GlobalConfig

    # import fake classes from our injected modules
    from server.lib.FileManager import FileManager as FM
    from server.lib.FinancialDataManager import FinancialDataManager as FDM

    return GlobalConfig(
        file_manager=FM(),
        financial_data_manager=FDM(),  # type: ignore
        user_id=1,
        project_id=1,
    )


@pytest.fixture
def node_ctor(global_config):
    """Helper to construct node instances safely in tests.

    Usage: node = node_ctor(type_name, **kwargs)
    """
    from server.interpreter.nodes.base_node import BaseNode

    def _ctor(type_name: str, **data):
        # BaseNode.create_from_type will lookup the registry and instantiate
        return BaseNode.create_from_type(global_config, type_name, **data)

    return _ctor


@pytest.fixture(scope="session", autouse=True)
def _default_fake_wordcloud():
    """Ensure a safe Fake WordCloud is available during tests to avoid
    system font / image generation dependencies. Tests that need to assert
    specific WordCloud behaviour can still monkeypatch `wordcloud.WordCloud`.
    """
    try:
        import wordcloud as _wc_mod
    except Exception:
        _wc_mod = types.ModuleType("wordcloud")
        sys.modules["wordcloud"] = _wc_mod

    class FakeWordCloud:
        def __init__(self, *args, **kwargs):
            self._freqs = None
        def generate_from_frequencies(self, freqs):
            # store frequencies for optional inspection
            try:
                self._freqs = dict(freqs)
            except Exception:
                self._freqs = None
            return None
        def __array__(self):
            # return a minimal image-like array; prefer numpy if available
            try:
                import numpy as _np
                return (_np.ones((8, 8, 3), dtype=_np.uint8) * 255)
            except Exception:
                return [[255]]

    _wc_mod.WordCloud = FakeWordCloud # type: ignore[attr-defined]
    return FakeWordCloud
