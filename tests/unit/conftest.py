"""Fixtures for the pure-logic characterization tests.

photochess/ (repo root) is the single canonical implementation (Fase 2 of
the refactor). As of Fase 3, Android's app/src/main/python/photochess/ is a
byte-for-byte copy of it rather than an independent implementation (see
test_android_sync.py) — Android no longer has its own utils.py/pipeline.py.
"""
import importlib
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(REPO_ROOT))
import photochess.fen as _fen_module  # noqa: E402


@pytest.fixture
def photochess_fen():
    # photochess.fen.board_matrix_from_fen keeps a shared module-level
    # matrix mutated in place (preserved intentionally, see
    # photochess/fen.py) — reload for test isolation.
    importlib.reload(_fen_module)
    return _fen_module
