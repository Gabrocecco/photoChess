"""Generates tests/golden/fens.json: current pipeline output on every image in
test_images/, used as a regression baseline for the refactor.

Reproduces pipeline.main()'s logic exactly (same calls into utils.py) but with
save=False and YOLO outputs redirected outside the repo, so running this script
never touches tracked files other than the golden JSON itself.

Usage: python tests/golden/generate_baseline.py [--out PATH] [--yolo-project DIR]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import cv2
from PIL import Image
from ultralytics import YOLO

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
from utils import order_points, plot_grid_on_transformed_image, connect_square_to_detection


def run_pipeline_on_image(image_path, turn, model_pieces, model_corner, yolo_project):
    img_PIL = Image.open(image_path)
    numpy_array_original_image = np.asarray(img_PIL)

    results_pieces_original = model_pieces.predict(
        img_PIL, save=False, iou=0.2, show=False,
        project=str(yolo_project), name="on_original_perspective", exist_ok=True,
    )
    results = model_corner.predict(
        img_PIL, save=False, conf=0.001, iou=0.1, imgsz=640, max_det=4, show=False,
        project=str(yolo_project), name="corners_detects", exist_ok=True,
    )

    boxes = results[0].boxes
    arr = boxes.xywh.numpy()
    points = arr[:, 0:2]

    if len(points) != 4:
        return {"error": f"expected 4 corners, got {len(points)}"}

    corners = order_points(points)
    tl, tr, br, bl = corners[0], corners[1], corners[2], corners[3]

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    if maxWidth <= 0 or maxHeight <= 0:
        return {"error": "degenerate warp size"}

    dst = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(corners, dst)
    warped = cv2.warpPerspective(numpy_array_original_image, M, (maxWidth, maxHeight))
    img_warped = Image.fromarray(warped, "RGB")

    boxes = results_pieces_original[0].boxes
    classes = boxes.cls
    arr = boxes.xywh.numpy()
    points = arr[:, 0:2]
    heights = arr[:, 3]
    points = np.float32(np.array(points))

    list_point_detects = []
    for point, height in zip(points, heights):
        p = np.float32(np.array([[point]]))
        new_point = cv2.perspectiveTransform(p, M)
        new_point = new_point[0][0]
        new_point[1] = new_point[1] + height * 0.4
        list_point_detects.append(new_point)

    ptsT, ptsL = plot_grid_on_transformed_image(img_warped)

    try:
        fen = connect_square_to_detection(list_point_detects, ptsT, ptsL, classes, turn)
    except KeyError as e:
        return {"error": f"unmapped class id {e}"}

    return {
        "fen": fen,
        "num_pieces_detected": int(len(points)),
        "num_corners_detected": 4,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(REPO_ROOT / "tests" / "golden" / "fens.json"))
    parser.add_argument("--yolo-project", default="/tmp/photochess_golden_yolo_out")
    parser.add_argument("--turn", default="w")
    args = parser.parse_args()

    model_pieces = YOLO(str(REPO_ROOT / "best_piecies.pt"))
    model_corner = YOLO(str(REPO_ROOT / "best_corners.pt"))

    test_images_dir = REPO_ROOT / "test_images"
    image_paths = sorted(
        p for p in test_images_dir.rglob("*")
        if p.suffix.lower() in (".jpg", ".jpeg", ".png") and "outputs" not in p.relative_to(test_images_dir).parts[:-1]
    )

    results = {}
    for path in image_paths:
        rel = str(path.relative_to(REPO_ROOT))
        print(f"Processing {rel} ...", file=sys.stderr)
        results[rel] = run_pipeline_on_image(path, args.turn, model_pieces, model_corner, args.yolo_project)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {len(results)} entries to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
