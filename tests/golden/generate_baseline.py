"""Generates tests/golden/fens.json: photochess.pipeline output on every
image in test_images/, used as a regression baseline for the refactor.

Excludes test_images/outputs/, which holds abandoned Harris-corner-detection
artifacts, not real board photos.

Usage: python tests/golden/generate_baseline.py [--out PATH]
"""
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
from photochess import detect, pipeline


def run_pipeline_on_image(path, turn, model_pieces, model_corner):
    image = pipeline.load_image_from_path(path)
    try:
        fen = pipeline.recognize_board(image, turn, model_pieces, model_corner)
    except ValueError as e:
        return {"error": str(e)}
    except KeyError as e:
        return {"error": f"unmapped class id {e}"}
    return {"fen": fen}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(REPO_ROOT / "tests" / "golden" / "fens.json"))
    parser.add_argument("--turn", default="w")
    args = parser.parse_args()

    model_pieces = detect.load_piece_model(str(REPO_ROOT / "best_piecies.pt"))
    model_corner = detect.load_corner_model(str(REPO_ROOT / "best_corners.pt"))

    test_images_dir = REPO_ROOT / "test_images"
    image_paths = sorted(
        p for p in test_images_dir.rglob("*")
        if p.suffix.lower() in (".jpg", ".jpeg", ".png") and "outputs" not in p.relative_to(test_images_dir).parts[:-1]
    )

    results = {}
    for path in image_paths:
        rel = str(path.relative_to(REPO_ROOT))
        print(f"Processing {rel} ...", file=sys.stderr)
        results[rel] = run_pipeline_on_image(path, args.turn, model_pieces, model_corner)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {len(results)} entries to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
