"""Thin wrapper around the two YOLO models (chessboard corners, chess
pieces). Isolates the ultralytics/torch dependency so geometry.py and fen.py
stay free of it.
"""
import numpy as np
from ultralytics import YOLO


def load_piece_model(weights_path):
    return YOLO(weights_path)


def load_corner_model(weights_path):
    return YOLO(weights_path)


def detect_pieces(model, image, **predict_kwargs):
    """Returns (points: Nx2 float32 box centers, heights: N box heights,
    classes: N tensor of class ids), matching results[0].boxes ordering.
    """
    results = model.predict(image, **predict_kwargs)
    boxes = results[0].boxes
    arr = boxes.xywh.numpy()
    points = np.float32(arr[:, 0:2])
    heights = arr[:, 3]
    return points, heights, boxes.cls


def detect_corners(model, image, **predict_kwargs):
    """Returns the raw (unordered) Nx2 box centers of detected corners."""
    results = model.predict(image, **predict_kwargs)
    boxes = results[0].boxes
    arr = boxes.xywh.numpy()
    return arr[:, 0:2]
