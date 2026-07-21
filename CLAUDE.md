# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

PhotoChess turns a photo of a physical chessboard into a FEN string, then into engine analysis. Two YOLOv8 models do the vision work (one detects the 4 board corners, one detects pieces); classical OpenCV geometry maps detections onto squares; python-chess renders the result and an online Stockfish API supplies best moves. It ships as an Android app that runs the *same* Python code on-device through Chaquopy.

## Repository layout: refactor in progress

**A repo-wide refactor is underway (tracked in-session, no separate design doc).** Status:

- **Done (Fase 0-2):** a regression safety net (`tests/`) was built first, then the desktop pipeline was consolidated. `photochess/` (repo root) is now the single canonical implementation of the recognition pipeline — `geometry.py` (order_points, homography, grid interpolation, pure), `fen.py` (create_fen, assign_pieces_to_squares, board_matrix_from_fen, edit_chessboard, pure), `detect.py` (YOLO wrapper), `pipeline.py` (orchestration: `recognize_board(image, turn, model_pieces, model_corner)`). Root [pipeline.py](pipeline.py) is now a thin CLI (`python pipeline.py <image> [w|b]`) over that package. The old root `utils.py` is gone — fully absorbed into `photochess/`.
- **Not done (Fase 3+):** [Android App/PhotoChess/app/src/main/python/](Android App/PhotoChess/app/src/main/python/) still has its own **independent, unmigrated copy** of `pipeline.py`/`utils.py` — this is what actually ships in the app today. Wiring Chaquopy to consume `photochess/` instead (e.g. via a `sourceSets` addition in `build.gradle`) needs a real Gradle/Android-SDK build to verify and hasn't been attempted. **A fix to the geometry or FEN logic still needs applying in both places** until that migration happens — check `tests/unit/*::*_matches_android_copy` tests, which cross-check `photochess/` against the Android copy and will fail if they silently drift apart.

Differences between the two copies (relevant until Fase 3 lands):

| | photochess/ (root) | Android |
|---|---|---|
| pipeline entry input | `PIL.Image` (`load_image_from_path`/`load_image_from_bytes` helpers) | JPEG `bytes` (`io.BytesIO`) |
| model loading | relative `"best_piecies.pt"` | absolute `/data/data/com.example.photochess/files/chaquopy/AssetFinder/app/*.pt` |
| engine/analysis fns | absent | `getbestmove`, `geteval`, `getboard`, `getfenfromedits` (not yet ported — see Fase 5 note below, blocked on the committed Lichess token) |

## The recognition pipeline

`photochess.pipeline.recognize_board(image, turn, model_pieces, model_corner)` — `turn` is `"w"` or `"b"` — runs these stages in order (the still-shipping Android `pipeline.main(bytes, turn)` runs the same steps inline, unconsolidated):

1. Piece detection on the **original, unwarped** photo (`best_piecies.pt`, `iou=0.2`). Detecting before warping is intentional: pieces are tall 3D objects and warping the image first distorts them badly.
2. Corner detection (`best_corners.pt`, `conf=0.001`, `max_det=4`) → exactly 4 points, ordered TL/TR/BR/BL by `geometry.order_points` (sum/diff-of-coordinates trick).
3. `geometry.compute_homography` (`cv2.getPerspectiveTransform`) → homography `M` → bird's-eye warp (`geometry.warp_image`).
4. Each piece's bounding-box center is pushed through `M` via `geometry.shift_point_to_square`, then shifted **down** by `height * 0.4` (marked `#PARAMETER SHIFT` in the pre-refactor source). This is the tuned magic constant that moves a detection from the middle of a standing piece to the square its base occupies. Changing it changes recognition accuracy more than anything else in the file.
5. `geometry.grid_points` interpolates 9 evenly spaced points along the top and left edges of the warped board.
6. `fen.assign_pieces_to_squares` builds 64 square centers, snaps each detection to the nearest one with a `scipy.spatial.KDTree`, and fills a 64-entry list. First detection wins a contested square; later ones are dropped.
7. `fen.create_fen` run-length-encodes the 8×8 matrix and appends `" {turn} KQkq - 0 1"`.

Castling rights, en-passant and move counters are always hardcoded in the FEN suffix — they are never recovered from the image. There is no defensive handling for degenerate corner detections (e.g. two of the four detected "corners" coinciding, producing a zero-width homography); on the OpenCV version this was verified against, `cv2.warpPerspective` silently no-ops on a zero-width `dsize` rather than raising, so the pipeline degrades to reporting an empty board instead of erroring — this is existing, unfixed behavior, not something the refactor introduced (verified by direct comparison against the pre-refactor source, see the Fase 2 commit message).

### Class-index mapping

`fen.CLASS_ID_TO_FEN_PIECE` maps YOLO class ids `1..12` → FEN letters, but `dataset_piecies/data.yaml` declares `nc: 13` with class `0` being a generic `'bishop'`. Class 0 is unmapped, so a class-0 detection raises `KeyError`. If you retrain or swap datasets, this mapping is the thing that breaks.

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

Training is not done in this repo — it runs in Colab via [yoloTrainingColab.ipynb](yoloTrainingColab.ipynb) (`yolo train model=yolov8n.pt data=.../data.yaml epochs=200 imgsz=640`) against a Drive-mounted dataset; results were downloaded into `training_output/` and the chosen weights promoted to `best_corners.pt` / `best_piecies.pt`.

## Testing (refactor safety net)

There was no test suite before the ongoing refactor; `tests/` exists to pin *current* behavior — bugs included — so refactor steps are checked against it rather than judged.

```bash
python -m pytest tests/unit              # pure-logic characterization tests, no ML deps needed, <1s
python tests/golden/check_baseline.py    # reruns photochess.pipeline on test_images/, diffs vs tests/golden/fens.json
sha256sum -c tests/golden/weights.sha256 # confirms best_corners.pt / best_piecies.pt haven't changed
```

`tests/golden/fens.json` is the FEN output on every real board photo under `test_images/` (excluding `test_images/outputs/`, which holds abandoned Harris-corner-detection artifacts, not board photos), verified two ways before being trusted: bit-for-bit deterministic across repeated runs on CPU, and cross-checked entry-by-entry against the literal, unmodified pre-refactor `pipeline.main()` (not just against itself) — that second check is what caught and fixed a bug in the *baseline generator itself* (see the Fase 2 commit). `tests/unit/` exercises `photochess.geometry`/`photochess.fen` directly; most tests also cross-check against the still-shipping Android `utils.py` copy (`*_matches_android_copy`), including `test_editing.py::test_get_chessboard_matrix_from_fen_leaks_state_between_calls`, which pins the module-global state leak from "Known rough edges" below on purpose. If a future commit fixes that bug, flip the assertion in that test rather than deleting it.

## Known rough edges

- `CameraActivity.usePhoto()` sends `R.drawable.testimage` to Python, **not** the bitmap just captured. The capture path is wired up but the hardcoded test image is what gets analyzed.
- Android `utils.py` mutates a module-level `chessboard_matrix` global inside `getChessboardMatrixfromFen`, so board state leaks between successive calls within one app session.
- A Lichess API token is committed in Android `utils.py`, `pipeline.py` and `getbestmove.py`. The `berserk`/Lichess path is dead code — analysis goes to `stockfish.online` over plain HTTP with the FEN interpolated unescaped into the URL.
- `constants.py` is empty; `getbestmove.py` is a superseded standalone copy of the engine functions.
- `non_production_archive/` (175 MB) holds abandoned Harris/contour corner-detection experiments, not part of the working pipeline — not yet removed from tracking, unlike the generated-output dirs `.gitignore` now excludes. `dataset_corners_labeled/`, `dataset_piecies/`, and `training_output/` are also still fully tracked (not yet moved to Git LFS or an external download step).
