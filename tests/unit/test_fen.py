"""Characterization tests for photochess.fen.create_fen (run-length encoding
of the 64-cell board into FEN). Root and Android utils.py used to share this
exact function (same signature); getbestmove.py has a superseded,
differently-signed copy (create_fen(matrix) with no turn arg) that was dead
code even before the refactor — pipeline.py imported create_fen from
utils.py, never from getbestmove.py.
"""
from photochess import fen


def _empty_board():
    return [""] * 64


def test_create_fen_empty_board():
    result = fen.create_fen(_empty_board(), "w")
    assert result == "8/8/8/8/8/8/8/8 w KQkq - 0 1"


def test_create_fen_starting_position():
    board = list(
        "rnbqkbnr"
        "pppppppp"
        "        "
        "        "
        "        "
        "        "
        "PPPPPPPP"
        "RNBQKBNR"
    )
    board = [c if c != " " else "" for c in board]

    result = fen.create_fen(board, "w")

    assert result == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def test_create_fen_mixed_run_lengths():
    row = ["", "", "P", "", "", "", "", ""]
    board = row + [""] * 56

    result = fen.create_fen(board, "b")

    assert result.split("/")[0] == "2P5"
    assert result.endswith(" b KQkq - 0 1")


def test_create_fen_matches_android_copy(utils_android):
    row1 = ["r", "", "b", "q", "k", "b", "n", "r"]
    row2 = ["p", "p", "p", "p", "", "p", "p", "p"]
    board = row1 + row2 + [""] * 48

    new_fen = fen.create_fen(board, "w")
    android_fen = utils_android.create_fen(board, "w")

    assert new_fen == android_fen


def test_assign_pieces_to_squares_single_piece():
    ptsT, ptsL = _grid()
    # class id 10 -> 'P' (white pawn), placed near the a8 square (index 0)
    points = [(ptsT[7][0] + 5, ptsL[0][1] + 5)]
    classes = _FakeClasses([10])

    result = fen.assign_pieces_to_squares(points, ptsT, ptsL, classes)

    assert result[0] == "P"
    assert result.count("P") == 1
    assert all(c == "" for c in result[1:])


def test_assign_pieces_to_squares_first_detection_wins_contested_square():
    ptsT, ptsL = _grid()
    center = (ptsT[7][0] + 5, ptsL[0][1] + 5)
    points = [center, center]  # both land on the same square
    classes = _FakeClasses([10, 1])  # 'P' then 'b'

    result = fen.assign_pieces_to_squares(points, ptsT, ptsL, classes)

    assert result[0] == "P"


def _grid():
    from photochess import geometry
    return geometry.grid_points(80, 80)


class _FakeClasses:
    """Mimics the subset of ultralytics Boxes.cls used by assign_pieces_to_squares."""
    def __init__(self, values):
        self._values = values

    def __getitem__(self, index):
        return _FakeTensor(self._values[index])


class _FakeTensor:
    def __init__(self, value):
        self._value = value

    def item(self):
        return self._value
