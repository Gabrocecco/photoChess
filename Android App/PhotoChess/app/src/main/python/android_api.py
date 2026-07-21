"""Chaquopy-facing facade. The five function names below are the Android
app's public API — Java loads this module as
`Python.getInstance().getModule("android_api")` (see CameraActivity.java and
AnalyzeActivity.java) and calls them by string name via callAttr(). Renamed
from this directory's old pipeline.py; if you rename anything here, update
those two Java call sites too (search for `getModule("android_api")`).

Delegates board recognition to the photochess/ subdirectory here, which is
a byte-for-byte copy of the repo-root photochess/ package (verified by
tests/unit/test_android_sync.py) rather than a Chaquopy sourceSets
reference to the repo root — reaching outside app/src/main/python/ risks
bundling the rest of the repo (datasets, archives) into the APK, which
wasn't something that could be verified with a real Gradle build in the
environment this refactor was done in. See CLAUDE.md for how to keep the
copy in sync. Stockfish analysis and SVG rendering stay Android-only, in
engine.py.
"""
from photochess import detect, fen, pipeline
from engine import getboard, getbestmove, geteval  # noqa: F401  (re-exported for Java callAttr)

MODEL_DIR = "/data/data/com.example.photochess/files/chaquopy/AssetFinder/app"


def main(array_image, turn):
    # Loads both models fresh on every call, matching the pre-refactor
    # Android pipeline.py exactly (no caching) — not the most efficient,
    # but changing that is a behavioral change this refactor didn't verify
    # on-device and so didn't make.
    model_pieces = detect.load_piece_model(f"{MODEL_DIR}/best_piecies.pt")
    model_corner = detect.load_corner_model(f"{MODEL_DIR}/best_corners.pt")
    image = pipeline.load_image_from_bytes(array_image)
    result = pipeline.recognize_board(image, turn, model_pieces, model_corner)
    print(result)
    return result


def getfenfromedits(fen_str, moves):
    chessboard, turn = fen.board_matrix_from_fen(fen_str)
    chessboard = fen.edit_chessboard(chessboard, moves)
    return fen.create_fen(chessboard, turn)
