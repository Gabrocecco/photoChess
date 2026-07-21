# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

PhotoChess turns a photo of a physical chessboard into a FEN string, then into engine analysis. Two YOLOv8 models do the vision work (one detects the 4 board corners, one detects pieces); classical OpenCV geometry maps detections onto squares; python-chess renders the result and an online Stockfish API supplies best moves. It ships as an Android app that runs the *same* Python code on-device through Chaquopy.

## Repository layout: refactor in progress

Top-level layout, after reorganizing what used to be loose files and datasets scattered directly at repo root:

```
photochess/           canonical recognition pipeline (see below)
Android App/          the Chaquopy Android app
models/               best_corners.pt, best_piecies.pt (promoted training output)
datasets/piecies/     roboflow-exported YOLO dataset for piece detection
datasets/corners_labeled/  roboflow-exported YOLO dataset for corner detection
training/             yoloTrainingColab.ipynb + training_output/ (past Colab runs)
test_images/          real board photos used by tests/golden/
tests/                golden + unit tests (the refactor's safety net)
docs/images/          README illustrations, including the pipeline walkthrough
pipeline.py           thin desktop CLI over photochess/
requirements.lock     pinned desktop Python env
```

`non_production_archive/` (abandoned Harris/contour experiments) still exists on disk but is no longer tracked — see "Known rough edges" below.

**A repo-wide refactor is underway (tracked in-session, no separate design doc).** Status:

- **Done (Fase 0-4):** `photochess/` (repo root) is the single canonical implementation of the recognition pipeline — `geometry.py` (order_points, homography, grid interpolation, pure), `fen.py` (create_fen, assign_pieces_to_squares, board_matrix_from_fen, edit_chessboard, pure), `detect.py` (YOLO wrapper), `pipeline.py` (orchestration: `recognize_board(image, turn, model_pieces, model_corner)`). Root [pipeline.py](pipeline.py) is a thin CLI (`python pipeline.py <image> [w|b]`) over that package. `Android App/PhotoChess/app/src/main/python/photochess/` is a **byte-for-byte copy** of it (enforced by `tests/unit/test_android_sync.py`) — Android no longer has its own independent recognition logic. `android_api.py` (the Chaquopy-facing facade Java actually calls) and `engine.py` (Stockfish/SVG, Android-only) replace what used to be Android's own `pipeline.py`/`utils.py`/`getbestmove.py`/`constants.py`, all now deleted. On the Java side, `BaseActivity` (chrome + Python-VM-startup helpers) and `PythonBridge` (a thin `callAttr` passthrough wrapping module lookup) replace three copies of the same boilerplate across `MainActivity`/`CameraActivity`/`AnalyzeActivity`. `CameraActivity.usePhoto()`'s capture bug is fixed (see "Known rough edges" history below).
- **The Android build was actually verified — including on a real (emulated) device, not just a build.** In an environment that started with no JDK, no Android SDK, and no emulator, self-provisioned everything needed (portable archives, no root/apt) and confirmed all of the following, in order:
  - `./gradlew assembleDebug` succeeded — a real, installable ~340 MB debug APK.
  - `./gradlew connectedDebugAndroidTest` ran **on a real headless x86_64 API 30 emulator (KVM-accelerated)** and passed — 5/5 tests green, including `PhotoChessRecognitionTest` (`app/src/androidTest/java/com/example/photochess/`), which calls `android_api.main()`/`getboard()`/`getfenfromedits()`/`geteval()` through `PythonBridge` exactly as the real activities do. `main()` ran the full on-device YOLO recognition pipeline against a real test photo (`app/src/androidTest/assets/test_board.jpg`, copied from `test_images/`) and returned `3kr3/3p3p/rb1n1p2/1pp3p1/P1Pq3n/1Q1NBb2/1P1PP1PN/RB2K3 w KQkq - 0 1` — **byte-for-byte identical** to the desktop golden baseline for that image (`tests/golden/fens.json`), despite the on-device stack being 5 major `torch` versions behind desktop (see below). `geteval()` also completed a real network call to `stockfish.online` from inside the emulator without error.
  - This confirms, with actual evidence rather than static reasoning: Chaquopy resolves the copied `photochess/` subpackage's relative imports correctly at runtime; `BaseActivity`'s ordering assumption about `getSupportActionBar()` needing `setContentView()` first holds (the app doesn't crash on launch); `PythonBridge`'s module lookup and `callAttr` passthrough work end-to-end; and the Fase 5 `geteval()`/`MATE_SENTINEL_EVALUATION` fix that was only caught by *calling* the code (not reading it) holds up under a real Android JVM, not just a desktop CPython interpreter standing in for one.
  - Toolchain used (reproducible, not required for normal contributors — a machine with Android Studio already has all of this): JDK 17 (Temurin); Android SDK cmdline-tools + platforms 30/34 + build-tools; a portable Python 3.11 (`uv python install`) exposed under several `python3.x`-named `PATH` symlinks, needed because this machine's only system Python (3.14) broke Chaquopy's bundled pip (`ModuleNotFoundError: No module named 'cgi'`, removed from the stdlib in 3.13) — **a stale Gradle daemon silently ignored the `PATH` fix on retry** (daemons cache their startup environment; `./gradlew --stop` was required); `system-images;android-30;google_apis;x86_64` (Google's own `sdkmanager` downloader stalled indefinitely partway through this one specific ~1.4 GB package for unclear reasons — fetched with a plain `curl` instead, at >3 MB/s, then extracted directly into `$ANDROID_HOME/system-images/`, which `sdkmanager --list_installed` picked up with no further steps needed); `avdmanager create avd` + `emulator -no-window -no-audio -gpu swiftshader_indirect -accel on` (KVM device permissions were already usable without any `usermod`).
  - **`ultralytics` had to be pinned** (`build.gradle`, now `ultralytics==8.3.100`, was unpinned `"ultralytics"`): unpinned, Chaquopy's pip resolved today's latest (8.4.103, same version the desktop `requirements.lock` uses), which depends on `polars`, which has no prebuilt Chaquopy wheel for Android and falls back to a source build requiring a Rust toolchain — unavailable and out of scope to provision. Confirmed via PyPI metadata that `polars` was *not* an `ultralytics` dependency as of 8.3.100 (last checked April 2025); it was added sometime between then and 8.4.103. **This would have broken the original, pre-refactor `build.gradle` identically if built today** — it is a preexisting unpinned-dependency problem the refactor happened to surface, not something introduced by it.
  - Chaquopy's own curated Android wheel index (`chaquo.com/pypi-13.1`) resolved dependencies far behind desktop's `requirements.lock`: **`torch==1.8.1`** (2021) vs. desktop's `2.13.0`, `numpy==1.19.5` vs `2.5.1`, `scipy==1.4.1` vs `1.18.0`, `opencv-python==4.5.1.48` vs `5.0.0.93` — all `cp38` (Python 3.8) ABI wheels; Chaquopy 15.0.1's supported on-device Python is 3.8, unrelated to whatever `buildPython` runs pip. This is exactly the divergence flagged in `requirements.lock`'s header, now confirmed with real version numbers — and, per the emulator test above, confirmed *not* to change the actual recognition output on the one image tested.
  - `matplotlib` is still pulled in (as a transitive `ultralytics` dependency) even though it's no longer in `build.gradle`'s explicit `pip { install ... }` block and no `photochess/`/`android_api.py`/`engine.py` code imports it — removing the explicit line doesn't shrink the APK the way "no longer a dependency of our code" might suggest.
  - **Still not exercised even now**: the actual UI (Activities were never touched via Espresso/UI Automator — `PhotoChessRecognitionTest` calls straight through `PythonBridge`, bypassing `CameraActivity`/`AnalyzeActivity`'s views and click handlers entirely) and real camera capture (no camera hardware on this emulator config). Those would need Espresso tests or a real device.
- **Fase 5 (explicit bug fixes, done as behavior changes on top of the logic-preserving refactor):**
  - The `stockfish.online` v1 API `getbestmove`/`geteval` used was **deprecated by the provider** (confirmed live: `{"success":false,"data":"This endpoint (v1) is no longer available..."}`) — best-move/eval were already broken before this refactor touched anything. `engine.py` now calls v2 (`api/s/v2.php`) instead: different HTTP method (GET, not POST — v2 returns 403 on POST), different response shape (`{success, evaluation, mate, bestmove, continuation}` instead of `{success, data}`), FEN and depth passed as proper encoded query params instead of raw string concatenation. Manually verified against the live endpoint for a normal position, a forced mate, and checkmate/stalemate (`continuation` is `null` there). This is a genuine behavior change, not a preserved one — there was no working v1 behavior left to preserve. Exercising `geteval()` against a live forced-mate position caught a bug *in this new code* before it was committed: an early version returned `"M3"`-style mate notation, but `AnalyzeActivity.analyzeMatch()` unconditionally does `Double.parseDouble(res.toString())` on any non-`"Error"` result — that would have thrown on-device on any mate position. Fixed by returning a large signed sentinel number (`±100.0`, see `MATE_SENTINEL_EVALUATION` in `engine.py`) instead, still a valid double string.
  - `photochess/fen.py`'s `board_matrix_from_fen` no longer shares a mutable matrix across calls — see "Known rough edges" history below, fixed and covered by `test_editing.py::test_get_chessboard_matrix_from_fen_does_not_leak_state_between_calls`.
  - `fen.assign_pieces_to_squares` now skips class-0 ("bishop", no color — see "Class-index mapping" below) detections instead of raising `KeyError`.
  - `CameraActivity.usePhoto()` now sends the bitmap `capturePhoto()` actually froze and stored (a new `capturedImage` field), not the hardcoded `R.drawable.testimage`. Re-fetching `previewView.getBitmap()` instead (the "obvious" one-line fix) would *also* have been wrong: the live camera preview keeps running under the frozen `imageView` even while `INVISIBLE`, so that would grab whatever the camera sees at confirm-time, not the frame the user actually confirmed.
- **Not done:** Lichess token revocation (still in git history — deleting the files that referenced it doesn't revoke it), and `AnalyzeActivity.analyzeMatch()`'s dead `String`-vs-`char` `.equals()` branch (see "Known rough edges" — cosmetic, no observable effect since the branch was already unreachable).

## The recognition pipeline

`photochess.pipeline.recognize_board(image, turn, model_pieces, model_corner)` — `turn` is `"w"` or `"b"` — runs these stages in order. Both the desktop CLI (`pipeline.py`) and the Android facade (`android_api.py`) call this same function now.

1. Piece detection on the **original, unwarped** photo (`models/best_piecies.pt`, `iou=0.2`). Detecting before warping is intentional: pieces are tall 3D objects and warping the image first distorts them badly.
2. Corner detection (`models/best_corners.pt`, `conf=0.001`, `max_det=4`) → exactly 4 points, ordered TL/TR/BR/BL by `geometry.order_points` (sum/diff-of-coordinates trick).
3. `geometry.compute_homography` (`cv2.getPerspectiveTransform`) → homography `M` → bird's-eye warp (`geometry.warp_image`).
4. Each piece's bounding-box center is pushed through `M` via `geometry.shift_point_to_square`, then shifted **down** by `height * 0.4` (marked `#PARAMETER SHIFT` in the pre-refactor source). This is the tuned magic constant that moves a detection from the middle of a standing piece to the square its base occupies. Changing it changes recognition accuracy more than anything else in the file.
5. `geometry.grid_points` interpolates 9 evenly spaced points along the top and left edges of the warped board.
6. `fen.assign_pieces_to_squares` builds 64 square centers, snaps each detection to the nearest one with a `scipy.spatial.KDTree`, and fills a 64-entry list. First detection wins a contested square; later ones are dropped.
7. `fen.create_fen` run-length-encodes the 8×8 matrix and appends `" {turn} KQkq - 0 1"`.

Castling rights, en-passant and move counters are always hardcoded in the FEN suffix — they are never recovered from the image. There is no defensive handling for degenerate corner detections (e.g. two of the four detected "corners" coinciding, producing a zero-width homography); on the OpenCV version this was verified against, `cv2.warpPerspective` silently no-ops on a zero-width `dsize` rather than raising, so the pipeline degrades to reporting an empty board instead of erroring — this is existing, unfixed behavior, not something the refactor introduced (verified by direct comparison against the pre-refactor source, see the Fase 2 commit message).

### Class-index mapping

`fen.CLASS_ID_TO_FEN_PIECE` maps YOLO class ids `1..12` → FEN letters, but `datasets/piecies/data.yaml` declares `nc: 13` with class `0` being a generic, colorless `'bishop'` — there's no FEN letter to map it to (a piece needs a color). `assign_pieces_to_squares` skips class-0 detections rather than erroring, same as if nothing had been detected on that square. If you retrain or swap datasets, this mapping is the thing to check.

## Android app

Java under [Android App/PhotoChess/app/src/main/java/com/example/photochess/](Android App/PhotoChess/app/src/main/java/com/example/photochess/): `MainActivity` (menu, starts the Python VM) → `CameraActivity` (CameraX preview, turn dialog, calls `main`) → `AnalyzeActivity` (SVG board, best move, eval, manual edits).

The Java↔Python boundary is `py.getModule("android_api")` plus `callAttr` by string name. These five names in `android_api.py` are the app's public API — renaming any of them compiles fine and fails at runtime:

`main(bytes, turn)` · `getboard(fen)` · `getbestmove(fen)` · `geteval(fen)` · `getfenfromedits(fen, moves)`

`getbestmove` and `getboard`/`geteval` are re-exported from `engine.py`; `main` and `getfenfromedits` are defined in `android_api.py` itself, delegating to `photochess/`.

`getbestmove` returns a `String[]` of SVG documents (one per ply of the principal variation, each with a green arrow), which `AnalyzeActivity` renders with AndroidSVG and steps through via the "next move" button. On any failure it returns the literal string `"Error"` and Java shows a toast — errors are signalled by that sentinel, not by exceptions.

Manual board edits use a small DSL built in `addEditString` and parsed by `fen.edit_chessboard`: `E4:White Pawn;A1:Empty`, semicolon-separated, piece names exactly as in `fen.EDIT_PIECE_CODES`.

## Build and run

Android (from `Android App/PhotoChess/`, Gradle 8.0, AGP 8.0.2, Chaquopy 15.0.1, minSdk 23):

```bash
./gradlew assembleDebug          # build APK
./gradlew installDebug           # build + install on connected device
./gradlew test                   # JVM unit tests (only the generated template test exists)
./gradlew connectedAndroidTest   # instrumented tests — needs a running device/emulator; see below
./gradlew clean
```

Chaquopy pip-installs `ultralytics`, `opencv-python`, `torch`, `scipy` etc. into the APK, so the first build is very slow (a clean `generateDebugPythonRequirements` took ~3-4 minutes even with everything cached from a prior attempt) and the APK is large (~340 MB debug). Native ABIs are pinned in `build.gradle` (`abiFilters`). As of this refactor the pip block also drops `berserk` (dead code, deleted with the old `getbestmove.py`) and `matplotlib` (no longer imported anywhere in `photochess/`, though still pulled in transitively — see above), adds `scipy` (`fen.py`'s `assign_pieces_to_squares` needs `scipy.spatial.KDTree` — this was already true of the pre-refactor Android `utils.py` too, and `scipy` was never declared here; whether that silently worked via transitive resolution or the app was already broken on a clean install wasn't chased down, since declaring it explicitly can only help), and **pins `ultralytics==8.3.100`** (was unpinned `"ultralytics"` — see the Fase 3/4 verification notes above for why this is required, not just tidiness).

Desktop pipeline — install the pinned environment from [requirements.lock](requirements.lock):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.lock
```

Use `--extra-index-url`, not `--index-url` — the latter replaces the default PyPI index instead of adding to it, and `download.pytorch.org` doesn't mirror the rest of PyPI (unrelated packages like `certifi` fail to resolve at all). `torch`/`torchvision` still specifically need that index — installing torchvision from default PyPI against a CPU-only torch build fails at import with `operator torchvision::nms does not exist`. The lock was pinned on Python 3.14 (the only interpreter available at the time); Chaquopy resolves the same package names independently against its own Android wheel index, so this lock does not guarantee identical behavior on-device — see the comment header in the file and the Fase 3/4 notes above for the confirmed real differences (`torch==1.8.1` vs `2.13.0`, etc).

Training is not done in this repo — it runs in Colab via [training/yoloTrainingColab.ipynb](training/yoloTrainingColab.ipynb) (`yolo train model=yolov8n.pt data=.../data.yaml epochs=200 imgsz=640`) against a Drive-mounted dataset; results were downloaded into `training/training_output/` and the chosen weights promoted to `models/best_corners.pt` / `models/best_piecies.pt`.

## Testing (refactor safety net)

There was no test suite before the ongoing refactor; `tests/` exists to pin *current* behavior — bugs included — so refactor steps are checked against it rather than judged.

```bash
python -m pytest tests/unit              # pure-logic characterization tests, no ML deps needed, <1s
python tests/golden/check_baseline.py    # reruns photochess.pipeline on test_images/, diffs vs tests/golden/fens.json
sha256sum -c tests/golden/weights.sha256 # confirms models/best_corners.pt / models/best_piecies.pt haven't changed
```

`tests/golden/fens.json` is the FEN output on every real board photo under `test_images/` (excluding `test_images/outputs/`, which holds abandoned Harris-corner-detection artifacts, not board photos), verified two ways before being trusted: bit-for-bit deterministic across repeated runs on CPU, and cross-checked entry-by-entry against the literal, unmodified pre-refactor `pipeline.main()` (not just against itself) — that second check is what caught and fixed a bug in the *baseline generator itself* (see the Fase 2 commit). `tests/unit/` exercises `photochess.geometry`/`photochess.fen` directly, including regression tests for the two bugs fixed in Fase 5 (`test_editing.py::test_get_chessboard_matrix_from_fen_does_not_leak_state_between_calls`, `test_fen.py::test_assign_pieces_to_squares_skips_unmapped_class_instead_of_raising`). `test_android_sync.py` checks the Android `photochess/` copy stays byte-identical to the root one (see the Fase 3 caveat above on why it's a copy at all — this means editing `photochess/` requires copying the changed file(s) into `Android App/PhotoChess/app/src/main/python/photochess/` too).

`app/src/androidTest/java/com/example/photochess/PhotoChessRecognitionTest.java` is an *instrumented* test — it runs inside a real Android process (device or emulator), not the JVM, via `./gradlew connectedDebugAndroidTest`. It calls `android_api.main()`/`getboard()`/`getfenfromedits()`/`geteval()` through `PythonBridge`, the same path the real Activities use, including a full on-device YOLO recognition pass against `app/src/androidTest/assets/test_board.jpg` (copied from `test_images/`, expected FEN pinned inline in the test and cross-referenced against `tests/golden/fens.json`). Confirmed passing on a real emulator — see the Fase 3/4 verification notes above.

## Known rough edges

- `AnalyzeActivity.analyzeMatch()`'s negative-score check is `res.toString().substring(0,1).equals('-')` — comparing a `String` to a `char` via `.equals()`, which autoboxes the `char` to `Character` and can never equal a `String`. That branch (labeling the score "BLACK") is dead code; pre-existing, not introduced by this refactor, not fixed — cosmetic (the final `else` still shows a plausible label) and low-risk to leave alone rather than touch speculatively.
- A Lichess API token was committed in the old Android `utils.py`/`pipeline.py`/`getbestmove.py` (all now deleted) for a `berserk`-based analysis path that was already dead code (commented out, never called). The token itself is still in **git history** — deleting the files didn't revoke it; that needs doing on Lichess's side.
- `non_production_archive/` (175 MB) holds abandoned Harris/contour corner-detection experiments, not part of the working pipeline. Untracked (added to `.gitignore`) rather than deleted from disk — it's still there locally and still in git history, it just no longer shows up in a fresh clone or the GitHub file browser. `datasets/piecies/`, `datasets/corners_labeled/`, and `training/training_output/` are legitimate provenance (labeled training data, past training runs) and are still fully tracked — not yet moved to Git LFS or an external download step, so a fresh clone of this repo is still large (~100+ MB of datasets alone).
