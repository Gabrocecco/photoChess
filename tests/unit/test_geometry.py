"""Characterization tests for order_points: pin current behavior so the
refactor (Fase 2, extracting a pure geometry module) can be verified against
it. Not a judgment on correctness — see CLAUDE.md for the TL/TR/BR/BL
ordering convention this function assumes.
"""
import numpy as np
import pytest


def test_order_points_axis_aligned_square(utils_root):
    # A simple, unambiguous square: sum-of-coords and diff-of-coords each
    # pick a distinct corner.
    pts = np.array([
        [10, 10],   # top-left    (min sum)
        [110, 10],  # top-right   (min diff: x - y)
        [110, 110], # bottom-right (max sum)
        [10, 110],  # bottom-left (max diff: x - y)
    ], dtype="float32")

    ordered = utils_root.order_points(pts)

    np.testing.assert_array_equal(ordered[0], [10, 10])
    np.testing.assert_array_equal(ordered[1], [110, 10])
    np.testing.assert_array_equal(ordered[2], [110, 110])
    np.testing.assert_array_equal(ordered[3], [10, 110])


def test_order_points_is_permutation_invariant(utils_root):
    pts = np.array([
        [110, 110],
        [10, 10],
        [10, 110],
        [110, 10],
    ], dtype="float32")

    ordered = utils_root.order_points(pts)

    np.testing.assert_array_equal(ordered[0], [10, 10])
    np.testing.assert_array_equal(ordered[1], [110, 10])
    np.testing.assert_array_equal(ordered[2], [110, 110])
    np.testing.assert_array_equal(ordered[3], [10, 110])


def test_order_points_root_and_android_agree(utils_root, utils_android):
    # Both copies of order_points must produce byte-identical output for the
    # refactor to be safe to consolidate into one module (Fase 2).
    pts = np.array([
        [87.0, 12.0],
        [412.0, 30.0],
        [430.0, 401.0],
        [70.0, 388.0],
    ], dtype="float32")

    root_result = utils_root.order_points(pts.copy())
    android_result = utils_android.order_points(pts.copy())

    np.testing.assert_array_equal(root_result, android_result)


def test_plot_grid_on_transformed_image_ptsT_ptsL_endpoints(utils_root):
    class FakeImage:
        size = (800, 400)  # (width, height)

    ptsT, ptsL = utils_root.plot_grid_on_transformed_image(FakeImage())

    assert len(ptsT) == 9
    assert len(ptsL) == 9
    # top edge runs left-to-right along y=0
    assert ptsT[0] == (0.0, 0.0)
    assert ptsT[-1] == (800.0, 0.0)
    # left edge runs top-to-bottom along x=0
    assert ptsL[0] == (0.0, 0.0)
    assert ptsL[-1] == (0.0, 400.0)
