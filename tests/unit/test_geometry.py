"""Characterization tests for photochess.geometry.order_points and
grid_points. See CLAUDE.md for the TL/TR/BR/BL ordering convention.
"""
import numpy as np

from photochess import geometry


def test_order_points_axis_aligned_square():
    # A simple, unambiguous square: sum-of-coords and diff-of-coords each
    # pick a distinct corner.
    pts = np.array([
        [10, 10],   # top-left    (min sum)
        [110, 10],  # top-right   (min diff: x - y)
        [110, 110], # bottom-right (max sum)
        [10, 110],  # bottom-left (max diff: x - y)
    ], dtype="float32")

    ordered = geometry.order_points(pts)

    np.testing.assert_array_equal(ordered[0], [10, 10])
    np.testing.assert_array_equal(ordered[1], [110, 10])
    np.testing.assert_array_equal(ordered[2], [110, 110])
    np.testing.assert_array_equal(ordered[3], [10, 110])


def test_order_points_is_permutation_invariant():
    pts = np.array([
        [110, 110],
        [10, 10],
        [10, 110],
        [110, 10],
    ], dtype="float32")

    ordered = geometry.order_points(pts)

    np.testing.assert_array_equal(ordered[0], [10, 10])
    np.testing.assert_array_equal(ordered[1], [110, 10])
    np.testing.assert_array_equal(ordered[2], [110, 110])
    np.testing.assert_array_equal(ordered[3], [10, 110])


def test_order_points_matches_android_copy(utils_android):
    # photochess.geometry.order_points must stay byte-identical to the
    # still-shipping Android copy until Fase 3 wires Android to photochess/.
    pts = np.array([
        [87.0, 12.0],
        [412.0, 30.0],
        [430.0, 401.0],
        [70.0, 388.0],
    ], dtype="float32")

    new_result = geometry.order_points(pts.copy())
    android_result = utils_android.order_points(pts.copy())

    np.testing.assert_array_equal(new_result, android_result)


def test_grid_points_endpoints():
    ptsT, ptsL = geometry.grid_points(800, 400)

    assert len(ptsT) == 9
    assert len(ptsL) == 9
    # top edge runs left-to-right along y=0
    assert ptsT[0] == (0.0, 0.0)
    assert ptsT[-1] == (800.0, 0.0)
    # left edge runs top-to-bottom along x=0
    assert ptsL[0] == (0.0, 0.0)
    assert ptsL[-1] == (0.0, 400.0)


def test_grid_points_matches_android_copy(utils_android):
    class FakeImage:
        size = (800, 400)

    expected_ptsT, expected_ptsL = utils_android.plot_grid_on_transformed_image(FakeImage())
    ptsT, ptsL = geometry.grid_points(800, 400)

    assert ptsT == expected_ptsT
    assert ptsL == expected_ptsL


def test_compute_homography_axis_aligned_square():
    corners = np.array([[0, 0], [100, 0], [100, 100], [0, 100]], dtype="float32")

    M, max_width, max_height = geometry.compute_homography(corners)

    assert max_width == 100
    assert max_height == 100
    # dst is (maxWidth - 1) x (maxHeight - 1), so an axis-aligned square maps
    # to a uniform 0.99 scale with no rotation/shear/translation.
    expected = np.array([[0.99, 0, 0], [0, 0.99, 0], [0, 0, 1]])
    np.testing.assert_allclose(M, expected, atol=1e-5)
