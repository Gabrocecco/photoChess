"""Characterization tests for the Android utils.py board-editing functions:
getChessboardMatrixfromFen and editchessboardwmoves.

Includes a deliberate test of the module-level state leak documented in
CLAUDE.md ("Known rough edges"): getChessboardMatrixfromFen mutates a single
shared `chessboard_matrix` global in place and only overwrites cells with a
piece, so cells that go from occupied to empty between two calls keep their
stale value. This is pinned as CURRENT behavior, not correct behavior — a
future fix (Fase 5 of the refactor plan) should flip this test rather than
silently changing behavior mid-refactor.
"""


def test_get_chessboard_matrix_from_fen_starting_position(utils_android):
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    matrix, turn = utils_android.getChessboardMatrixfromFen(fen)

    assert turn == "w"
    assert list(matrix[0]) == ["r", "n", "b", "q", "k", "b", "n", "r"]
    assert list(matrix[1]) == ["p"] * 8
    assert list(matrix[6]) == ["P"] * 8
    assert list(matrix[7]) == ["R", "N", "B", "Q", "K", "B", "N", "R"]
    for row in matrix[2:6]:
        assert list(row) == [""] * 8


def test_get_chessboard_matrix_from_fen_black_turn(utils_android):
    _, turn = utils_android.getChessboardMatrixfromFen(
        "8/8/8/8/8/8/8/8 b KQkq - 0 1"
    )
    assert turn == "b"


def test_get_chessboard_matrix_from_fen_leaks_state_between_calls(utils_android):
    # KNOWN BUG, pinned intentionally: parsing a full board, then an empty
    # one, does not clear the board because emptied cells are never written.
    full_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    empty_fen = "8/8/8/8/8/8/8/8 w KQkq - 0 1"

    utils_android.getChessboardMatrixfromFen(full_fen)
    matrix_after_empty, _ = utils_android.getChessboardMatrixfromFen(empty_fen)

    # A correct implementation would make this an all-empty board; today it
    # still shows the starting position because nothing clears stale cells.
    assert list(matrix_after_empty[0]) == ["r", "n", "b", "q", "k", "b", "n", "r"]
    assert list(matrix_after_empty[6]) == ["P"] * 8


def test_edit_chessboard_with_moves_sets_piece(utils_android):
    board = [["" for _ in range(8)] for _ in range(8)]

    result = utils_android.editchessboardwmoves(board, "E4:White Pawn")

    # E -> column 4, rank 4 -> dictCell[4] - 1 = row 4
    assert result[4][4] == "P"


def test_edit_chessboard_with_moves_clears_square(utils_android):
    board = [["" for _ in range(8)] for _ in range(8)]
    board[0][0] = "R"

    result = utils_android.editchessboardwmoves(board, "A8:Empty")

    # A -> column 0, rank 8 -> dictCell[8] - 1 = row 0
    assert result[0][0] == ""


def test_edit_chessboard_with_moves_multiple_semicolon_separated(utils_android):
    board = [["" for _ in range(8)] for _ in range(8)]

    result = utils_android.editchessboardwmoves(board, "A1:White Rook;H1:Black King")

    # A1 -> dictCell[1]-1=7, column 0 | H1 -> row 7, column 7
    assert result[7][0] == "R"
    assert result[7][7] == "k"
