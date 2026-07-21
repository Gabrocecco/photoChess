"""Orchestrates the full image -> FEN recognition pipeline: detect pieces on
the original photo, detect the 4 board corners, warp to a bird's-eye view,
project piece detections into that view, snap them to the 8x8 grid, encode
as FEN.

This is the single implementation behind what used to be two divergent
copies (repo-root pipeline.py and the Android Chaquopy pipeline.py) — see
CLAUDE.md for why they diverged (image-path vs. in-memory bytes input,
relative vs. Chaquopy-absolute weight paths, save=True vs. False). Those
differences are now caller-supplied arguments rather than forked source.
"""
import io

import numpy as np
from PIL import Image

from . import detect, fen, geometry

DEFAULT_PIECE_PREDICT_KWARGS = {"iou": 0.2, "save": False, "show": False}
DEFAULT_CORNER_PREDICT_KWARGS = {
    "conf": 0.001, "iou": 0.1, "imgsz": 640, "max_det": 4, "save": False, "show": False,
}


def load_image_from_path(path):
    return Image.open(path)


def load_image_from_bytes(data):
    return Image.open(io.BytesIO(data))


def recognize_board(image, turn, model_pieces, model_corner,
                     piece_predict_kwargs=None, corner_predict_kwargs=None):
    """image: a PIL.Image (already opened — see load_image_from_path/bytes).
    turn: "w" or "b", passed through verbatim into the output FEN.
    Returns a FEN string.
    """
    piece_kwargs = {**DEFAULT_PIECE_PREDICT_KWARGS, **(piece_predict_kwargs or {})}
    corner_kwargs = {**DEFAULT_CORNER_PREDICT_KWARGS, **(corner_predict_kwargs or {})}

    original_image_array = np.asarray(image)

    piece_points, piece_heights, piece_classes = detect.detect_pieces(model_pieces, image, **piece_kwargs)
    corner_points = detect.detect_corners(model_corner, image, **corner_kwargs)

    corners = geometry.order_points(corner_points)
    M, max_width, max_height = geometry.compute_homography(corners)
    warped_array = geometry.warp_image(original_image_array, M, max_width, max_height)
    warped_image = Image.fromarray(warped_array, "RGB")

    projected_points = [
        geometry.shift_point_to_square(point, height, M)
        for point, height in zip(piece_points, piece_heights)
    ]

    ptsT, ptsL = geometry.grid_points(warped_image.width, warped_image.height)

    chessboard_list = fen.assign_pieces_to_squares(projected_points, ptsT, ptsL, piece_classes)
    return fen.create_fen(chessboard_list, turn)
