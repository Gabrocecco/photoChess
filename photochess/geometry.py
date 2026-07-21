"""Pure perspective-geometry helpers: corner ordering, homography, grid
interpolation. No I/O, no plotting — everything here is array-in, array-out,
so it can be unit tested without torch/ultralytics.

Consolidates what used to be two copies of order_points/
plot_grid_on_transformed_image (repo-root utils.py and the Android
Chaquopy utils.py). plot_grid_on_transformed_image is renamed to
grid_points() and no longer takes an image object or allocates a matplotlib
Figure — that allocation had no effect on its return value (nothing was ever
drawn to it on the live code path; the plt.savefig() call was already
commented out), confirmed by tests/golden/check_baseline.py before and after
this change.
"""
import cv2
import numpy as np


def order_points(pts):
    """Orders 4 (x, y) points as [top-left, top-right, bottom-right, bottom-left]."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


def grid_points(width, height):
    """Returns (ptsT, ptsL): 9 evenly spaced points along the top and left
    edges of a width x height rectangle, used to build the 8x8 square grid.
    """
    corners = np.array([[0, 0], [width, 0], [0, height], [width, height]])
    corners = order_points(corners)

    TL = corners[0]
    BL = corners[3]
    TR = corners[1]
    BR = corners[2]

    def interpolate(xy0, xy1):
        x0, y0 = xy0
        x1, y1 = xy1
        dx = (x1 - x0) / 8
        dy = (y1 - y0) / 8
        return [(x0 + i * dx, y0 + i * dy) for i in range(9)]

    ptsT = interpolate(TL, TR)
    ptsL = interpolate(TL, BL)
    return ptsT, ptsL


def compute_homography(corners):
    """corners: 4x2 float32 array ordered [TL, TR, BR, BL] (as returned by
    order_points). Returns (M, max_width, max_height) for warping the
    quadrilateral onto an axis-aligned max_width x max_height rectangle.
    """
    tl, tr, br, bl = corners[0], corners[1], corners[2], corners[3]

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    max_width = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_height = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1],
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(corners, dst)
    return M, max_width, max_height


def warp_image(image_array, M, max_width, max_height):
    return cv2.warpPerspective(image_array, M, (max_width, max_height))


def shift_point_to_square(point, height, M):
    """Transforms a piece detection's (x, y) center through homography M,
    then shifts it down by height * 0.4 so it lands on the square the piece
    is standing on rather than the middle of the (tall) piece sprite.
    height * 0.4 is a tuned constant, not derived — see CLAUDE.md.
    """
    p = np.float32(np.array([[point]]))
    new_point = cv2.perspectiveTransform(p, M)[0][0]
    new_point[1] = new_point[1] + height * 0.4
    return new_point
