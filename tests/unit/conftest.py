"""Loads the two divergent utils.py copies (repo root and Android) under
distinct module names, since they can't both be imported as `utils`.
See CLAUDE.md for why the duplication exists.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT_UTILS_PATH = REPO_ROOT / "utils.py"
ANDROID_UTILS_PATH = REPO_ROOT / "Android App" / "PhotoChess" / "app" / "src" / "main" / "python" / "utils.py"


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def utils_root():
    return _load_module("utils_root", ROOT_UTILS_PATH)


@pytest.fixture
def utils_android():
    # Re-loaded fresh per test (not session-scoped): this module keeps a
    # mutable module-level `chessboard_matrix` global that leaks state
    # between calls (see test_editing.py), so tests must not share an
    # instance unless that leak is exactly what's being tested.
    return _load_module("utils_android", ANDROID_UTILS_PATH)
