"""Fixtures for the pure-logic characterization tests.

photochess/ (repo root) is the single canonical implementation (Fase 2 of
the refactor). The Android Chaquopy copy under app/src/main/python/utils.py
is still the one actually shipping in the app (Fase 3, wiring Android to
photochess/, hasn't happened yet — see CLAUDE.md) so it's loaded separately
here and cross-checked for behavioral parity against photochess/.
"""
import importlib
import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ANDROID_UTILS_PATH = REPO_ROOT / "Android App" / "PhotoChess" / "app" / "src" / "main" / "python" / "utils.py"

sys.path.insert(0, str(REPO_ROOT))
import photochess.fen as _fen_module  # noqa: E402


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def utils_android():
    # Re-loaded fresh per test (not session-scoped): this module keeps a
    # mutable module-level `chessboard_matrix` global that leaks state
    # between calls (see test_editing.py), so tests must not share an
    # instance unless that leak is exactly what's being tested.
    return _load_module("utils_android", ANDROID_UTILS_PATH)


@pytest.fixture
def photochess_fen():
    # photochess.fen.board_matrix_from_fen has the same kind of shared
    # module-level state as utils_android (preserved intentionally, see
    # photochess/fen.py) — reload for the same isolation reason.
    importlib.reload(_fen_module)
    return _fen_module
