"""Fixtures for the pure-logic characterization tests.

photochess/ (repo root) is the single canonical implementation (Fase 2 of
the refactor). As of Fase 3, Android's app/src/main/python/photochess/ is a
byte-for-byte copy of it rather than an independent implementation (see
test_android_sync.py) — Android no longer has its own utils.py/pipeline.py.
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(REPO_ROOT))
from photochess import fen as _fen_module  # noqa: E402


@pytest.fixture
def photochess_fen():
    return _fen_module
