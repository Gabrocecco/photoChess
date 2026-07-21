"""Characterization tests for photochess.fen.board_matrix_from_fen and
edit_chessboard (ported from the Android-only utils.py, pre-Fase-3; the
desktop copy never had these before the refactor).
"""


def test_get_chessboard_matrix_from_fen_starting_position(photochess_fen):
    fen_str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    matrix, turn = photochess_fen.board_matrix_from_fen(fen_str)

    assert turn == "w"
    assert list(matrix[0]) == ["r", "n", "b", "q", "k", "b", "n", "r"]
    assert list(matrix[1]) == ["p"] * 8
    assert list(matrix[6]) == ["P"] * 8
    assert list(matrix[7]) == ["R", "N", "B", "Q", "K", "B", "N", "R"]
    for row in matrix[2:6]:
        assert list(row) == [""] * 8


def test_get_chessboard_matrix_from_fen_black_turn(photochess_fen):
    _, turn = photochess_fen.board_matrix_from_fen("8/8/8/8/8/8/8/8 b KQkq - 0 1")
    assert turn == "b"


def test_get_chessboard_matrix_from_fen_does_not_leak_state_between_calls(photochess_fen):
    # Regression test for a fixed bug (see git history / photochess/fen.py):
    # board_matrix_from_fen used to mutate a single shared module-level
    # matrix in place, so parsing a full board followed by an empty one
    # left the board showing stale pieces instead of actually clearing.
    full_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    empty_fen = "8/8/8/8/8/8/8/8 w KQkq - 0 1"

    photochess_fen.board_matrix_from_fen(full_fen)
    matrix_after_empty, _ = photochess_fen.board_matrix_from_fen(empty_fen)

    for row in matrix_after_empty:
        assert list(row) == [""] * 8


def test_edit_chessboard_sets_piece(photochess_fen):
    board = [["" for _ in range(8)] for _ in range(8)]

    result = photochess_fen.edit_chessboard(board, "E4:White Pawn")

    # E -> column 4, rank 4 -> RANK_TO_ROW[4] - 1 = row 4
    assert result[4][4] == "P"


def test_edit_chessboard_clears_square(photochess_fen):
    board = [["" for _ in range(8)] for _ in range(8)]
    board[0][0] = "R"

    result = photochess_fen.edit_chessboard(board, "A8:Empty")

    # A -> column 0, rank 8 -> RANK_TO_ROW[8] - 1 = row 0
    assert result[0][0] == ""


def test_edit_chessboard_multiple_semicolon_separated(photochess_fen):
    board = [["" for _ in range(8)] for _ in range(8)]

    result = photochess_fen.edit_chessboard(board, "A1:White Rook;H1:Black King")

    # A1 -> RANK_TO_ROW[1]-1=7, column 0 | H1 -> row 7, column 7
    assert result[7][0] == "R"
    assert result[7][7] == "k"
