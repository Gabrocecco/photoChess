"""Characterization tests for create_fen (run-length encoding of the 64-cell
board into FEN). Root and Android utils.py share this exact function
(same signature); getbestmove.py has a superseded, differently-signed copy
(create_fen(matrix) with no turn arg) that is dead code — pipeline.py
imports create_fen from utils.py, not from getbestmove.py.
"""


def _empty_board():
    return [""] * 64


def test_create_fen_empty_board(utils_root):
    fen = utils_root.create_fen(_empty_board(), "w")
    assert fen == "8/8/8/8/8/8/8/8 w KQkq - 0 1"


def test_create_fen_starting_position(utils_root):
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

    fen = utils_root.create_fen(board, "w")

    assert fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def test_create_fen_mixed_run_lengths(utils_root):
    row = ["", "", "P", "", "", "", "", ""]
    board = row + [""] * 56

    fen = utils_root.create_fen(board, "b")

    assert fen.split("/")[0] == "2P5"
    assert fen.endswith(" b KQkq - 0 1")


def test_create_fen_root_and_android_agree(utils_root, utils_android):
    row1 = ["r", "", "b", "q", "k", "b", "n", "r"]
    row2 = ["p", "p", "p", "p", "", "p", "p", "p"]
    board = row1 + row2 + [""] * 48

    root_fen = utils_root.create_fen(board, "w")
    android_fen = utils_android.create_fen(board, "w")

    assert root_fen == android_fen
