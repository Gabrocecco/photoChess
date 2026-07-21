"""CLI entry point for the desktop recognition pipeline. The actual pipeline
implementation lives in photochess/ (photochess.pipeline.recognize_board);
this used to be a full standalone copy of that logic (see CLAUDE.md/git
history) plus a second divergent copy under
Android App/PhotoChess/app/src/main/python/.

Usage: python pipeline.py <image_path> [w|b]
"""
import sys

from photochess import detect, pipeline

WEIGHTS_DIR = "models"


def main(image_path, turn="w"):
    model_pieces = detect.load_piece_model(f"{WEIGHTS_DIR}/best_piecies.pt")
    model_corner = detect.load_corner_model(f"{WEIGHTS_DIR}/best_corners.pt")
    image = pipeline.load_image_from_path(image_path)
    fen = pipeline.recognize_board(image, turn, model_pieces, model_corner)
    print(fen)
    return fen


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <image_path> [w|b]", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "w")
