"""Regenerates the pipeline output on test_images/ and diffs it against the
committed tests/golden/fens.json baseline. Exit code 0 means "logic
unchanged"; run this after every refactor step (Fase 0 of the refactor
plan in CLAUDE.md).

Usage: python tests/golden/check_baseline.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = REPO_ROOT / "tests" / "golden" / "fens.json"


def main():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        current_path = Path(tmp.name)

    subprocess.run(
        [sys.executable, str(REPO_ROOT / "tests" / "golden" / "generate_baseline.py"), "--out", str(current_path)],
        check=True,
    )

    baseline = json.loads(BASELINE_PATH.read_text())
    current = json.loads(current_path.read_text())
    current_path.unlink()

    if baseline == current:
        print("OK: pipeline output matches tests/golden/fens.json exactly.")
        return 0

    baseline_keys = set(baseline)
    current_keys = set(current)
    if baseline_keys != current_keys:
        print("MISMATCH: image set differs.")
        print(" missing:", sorted(baseline_keys - current_keys))
        print(" extra:  ", sorted(current_keys - baseline_keys))

    diffs = [k for k in sorted(baseline_keys & current_keys) if baseline[k] != current[k]]
    if diffs:
        print(f"MISMATCH: {len(diffs)} image(s) changed output:")
        for k in diffs:
            print(f"  {k}")
            print(f"    before: {baseline[k]}")
            print(f"    after:  {current[k]}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
