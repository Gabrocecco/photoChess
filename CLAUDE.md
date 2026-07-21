# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

PhotoChess turns a photo of a physical chessboard into a FEN string, then into engine analysis. Two YOLOv8 models do the vision work (one detects the 4 board corners, one detects pieces); classical OpenCV geometry maps detections onto squares; python-chess renders the result and an online Stockfish API supplies best moves. It ships as an Android app that runs the *same* Python code on-device through Chaquopy.

## Repository layout: the code exists twice

There are two near-identical copies of the Python pipeline, and this is the single most important thing to know before editing:

- Repo root — [pipeline.py](pipeline.py), [utils.py](utils.py). The desktop/research version, used for experimenting against `test_images/` and the datasets.
- [Android App/PhotoChess/app/src/main/python/](Android App/PhotoChess/app/src/main/python/) — `pipeline.py`, `utils.py`, plus copies of both `.pt` weights. This is what actually ships.

They have diverged deliberately in a few places, so **do not blindly copy one over the other**:

| | root | Android |
|---|---|---|
| `main()` input | image file path | JPEG `bytes` (`io.BytesIO`) |
| model loading | relative `"best_piecies.pt"` | absolute `/data/data/com.example.photochess/files/chaquopy/AssetFinder/app/*.pt` |
| YOLO `save=` | `True` (writes to `yolo_output_final_warped/`) | `False` |
| engine/analysis fns | absent | `getbestmove`, `geteval`, `getboard`, `getfenfromedits` |

A fix to the geometry or FEN logic almost always needs applying in both `utils.py` files.

## The recognition pipeline

`pipeline.main(image, turn)` — `turn` is `"w"` or `"b"` — runs these stages in order:

1. Piece detection on the **original, unwarped** photo (`best_piecies.pt`, `iou=0.2`). Detecting before warping is intentional: pieces are tall 3D objects and warping the image first distorts them badly.
2. Corner detection (`best_corners.pt`, `conf=0.001`, `max_det=4`) → exactly 4 points, ordered TL/TR/BR/BL by `order_points` (sum/diff-of-coordinates trick).
3. `cv2.getPerspectiveTransform` → homography `M` → bird's-eye warp.
4. Each piece's bounding-box center is pushed through `M`, then shifted **down** by `height * 0.4` (marked `#PARAMETER SHIFT` in the source). This is the tuned magic constant that moves a detection from the middle of a standing piece to the square its base occupies. Changing it changes recognition accuracy more than anything else in the file.
5. `plot_grid_on_transformed_image` interpolates 9 evenly spaced points along the top and left edges of the warped board (it does **not** plot anything despite the name).
6. `connect_square_to_detection` builds 64 square centers, snaps each detection to the nearest one with a `scipy.spatial.KDTree`, and fills a 64-entry list. First detection wins a contested square; later ones are dropped.
7. `create_fen` run-length-encodes the 8×8 matrix and appends `" {turn} KQkq - 0 1"`.

Castling rights, en-passant and move counters are always hardcoded in the FEN suffix — they are never recovered from the image.

### Class-index mapping

`dictFenPieces` (Android) / `dictPieces` (root) maps YOLO class ids `1..12` → FEN letters, but `dataset_piecies/data.yaml` declares `nc: 13` with class `0` being a generic `'bishop'`. Class 0 is unmapped, so a class-0 detection raises `KeyError`. If you retrain or swap datasets, this mapping is the thing that breaks.

## Android app

Java under [Android App/PhotoChess/app/src/main/java/com/example/photochess/](Android App/PhotoChess/app/src/main/java/com/example/photochess/): `MainActivity` (menu, starts the Python VM) → `CameraActivity` (CameraX preview, turn dialog, calls `main`) → `AnalyzeActivity` (SVG board, best move, eval, manual edits).

The Java↔Python boundary is `py.getModule("pipeline")` plus `callAttr` by string name. These five names in the Android `pipeline.py` are the app's public API — renaming any of them compiles fine and fails at runtime:

`main(bytes, turn)` · `getboard(fen)` · `getbestmove(fen)` · `geteval(fen)` · `getfenfromedits(fen, moves)`

`getbestmove` returns a `String[]` of SVG documents (one per ply of the principal variation, each with a green arrow), which `AnalyzeActivity` renders with AndroidSVG and steps through via the "next move" button. On any failure it returns the literal string `"Error"` and Java shows a toast — errors are signalled by that sentinel, not by exceptions.

Manual board edits use a small DSL built in `addEditString` and parsed by `editchessboardwmoves`: `E4:White Pawn;A1:Empty`, semicolon-separated, piece names exactly as in `dictEditPieces`.

## Build and run

Android (from `Android App/PhotoChess/`, Gradle 8.0, AGP 8.0.2, Chaquopy 15.0.1, minSdk 23):

```bash
./gradlew assembleDebug          # build APK
./gradlew installDebug           # build + install on connected device
./gradlew test                   # JVM unit tests (only the generated template test exists)
./gradlew connectedAndroidTest   # instrumented tests (template only)
./gradlew clean
```

Chaquopy pip-installs `ultralytics`, `opencv-python`, `torch`, `matplotlib` etc. into the APK, so the first build is very slow and the APK is large. Native ABIs are pinned in `build.gradle` (`abiFilters`).

Desktop pipeline — install the pinned environment from [requirements.lock](requirements.lock):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install --index-url https://download.pytorch.org/whl/cpu -r requirements.lock
```

`torch`/`torchvision` must come from that same PyTorch index — installing torchvision from default PyPI against a CPU-only torch build fails at import with `operator torchvision::nms does not exist`. The lock was pinned on Python 3.14 (the only interpreter available at the time); Chaquopy resolves the same package names independently against its own Android wheel index, so this lock does not guarantee identical behavior on-device — see the comment header in the file.

Note that root [pipeline.py:135-136](pipeline.py#L135-L136) calls `main()` at import time against a hardcoded Windows-style path, so `import pipeline` executes a full inference run. Edit those lines (or guard them with `if __name__ == "__main__":`) rather than fighting it.

Training is not done in this repo — it runs in Colab via [yoloTrainingColab.ipynb](yoloTrainingColab.ipynb) (`yolo train model=yolov8n.pt data=.../data.yaml epochs=200 imgsz=640`) against a Drive-mounted dataset; results were downloaded into `training_output/` and the chosen weights promoted to `best_corners.pt` / `best_piecies.pt`.

## Testing (refactor safety net)

There was no test suite before the ongoing refactor (see the plan discussed in-session); `tests/` now exists purely to pin *current* behavior — bugs included — so refactor steps can be checked against it rather than judged.

```bash
python -m pytest tests/unit              # pure-logic characterization tests, no ML deps needed, <1s
python tests/golden/check_baseline.py    # reruns the full YOLO pipeline on test_images/, diffs vs tests/golden/fens.json
sha256sum -c tests/golden/weights.sha256 # confirms best_corners.pt / best_piecies.pt haven't changed
```

`tests/golden/fens.json` is the FEN output of the *unmodified* pipeline on every real board photo under `test_images/` (excluding `test_images/outputs/`, which holds abandoned Harris-corner-detection artifacts, not board photos). Confirmed bit-for-bit deterministic across repeated runs on CPU. `tests/unit/` exercises `order_points`, `create_fen`, `plot_grid_on_transformed_image`, `getChessboardMatrixfromFen` and `editchessboardwmoves` directly — including `test_editing.py::test_get_chessboard_matrix_from_fen_leaks_state_between_calls`, which pins the module-global state leak from "Known rough edges" below on purpose. If a future commit fixes that bug, flip the assertion in that test rather than deleting it.

## Known rough edges

- `CameraActivity.usePhoto()` sends `R.drawable.testimage` to Python, **not** the bitmap just captured. The capture path is wired up but the hardcoded test image is what gets analyzed.
- Android `utils.py` mutates a module-level `chessboard_matrix` global inside `getChessboardMatrixfromFen`, so board state leaks between successive calls within one app session.
- A Lichess API token is committed in Android `utils.py`, `pipeline.py` and `getbestmove.py`. The `berserk`/Lichess path is dead code — analysis goes to `stockfish.online` over plain HTTP with the FEN interpolated unescaped into the URL.
- `constants.py` is empty; `getbestmove.py` is a superseded standalone copy of the engine functions.
- No `.gitignore`: datasets, 68 `runs/detect/predict*` output dirs, and a 4 MB notebook are all tracked. `non_production_archive/` holds abandoned Harris/contour corner-detection experiments — not part of the working pipeline.
