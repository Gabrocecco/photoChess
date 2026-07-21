"""Verifies Android App/PhotoChess/app/src/main/python/photochess/ is a
byte-for-byte copy of the repo-root photochess/ package.

Chaquopy bundles app/src/main/python/ as-is; reaching outside it via a
custom sourceSets entry to share photochess/ directly risks pulling
unrelated repo content (datasets, archives) into the APK and wasn't
something that could be verified with a real Gradle build in the
environment this refactor was done in (see CLAUDE.md, Fase 3). Until that's
revisited, the Android copy is kept in sync by hand — this test is the
tripwire: it fails the moment the two drift, in either direction.

To resync after editing repo-root photochess/:
    cp photochess/*.py "Android App/PhotoChess/app/src/main/python/photochess/"
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = REPO_ROOT / "photochess"
ANDROID_COPY_DIR = REPO_ROOT / "Android App" / "PhotoChess" / "app" / "src" / "main" / "python" / "photochess"


def test_android_photochess_copy_is_byte_identical_to_source():
    source_files = {p.name: p for p in SOURCE_DIR.glob("*.py")}
    android_files = {p.name: p for p in ANDROID_COPY_DIR.glob("*.py")}

    assert source_files.keys() == android_files.keys(), (
        f"file sets differ: only in source={source_files.keys() - android_files.keys()}, "
        f"only in android copy={android_files.keys() - source_files.keys()}"
    )

    mismatches = [
        name for name, source_path in source_files.items()
        if source_path.read_bytes() != android_files[name].read_bytes()
    ]
    assert not mismatches, f"out of sync with repo-root photochess/: {mismatches}"
