"""FEN encoding/decoding and board editing. Pure logic — no I/O, no torch.

Consolidates repo-root utils.py and Android utils.py (which had identical
create_fen and connect_square_to_detection, renamed here to
assign_pieces_to_squares), plus the Android-only board-editing functions
(board_matrix_from_fen, edit_chessboard) that the desktop copy never had.

connect_square_to_detection's plt.scatter(point[0], point[1]) call is
dropped here: it plotted to a matplotlib global that nothing ever showed or
saved on the live code path, so it had no effect on the returned FEN —
confirmed by tests/golden/check_baseline.py before and after this change.
"""
import numpy as np
from scipy import spatial

CLASS_ID_TO_FEN_PIECE = {
    1: "b", 2: "k", 3: "n", 4: "p", 5: "q", 6: "r",
    7: "B", 8: "K", 9: "N", 10: "P", 11: "Q", 12: "R",
}

COLUMN_INDEX = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}

RANK_TO_ROW = {1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}

EDIT_PIECE_CODES = {
    "Empty": "0", "White Pawn": "P", "White Bishop": "B", "White Knight": "N",
    "White Rook": "R", "White Queen": "Q", "White King": "K", "Black Pawn": "p",
    "Black Bishop": "b", "Black Knight": "n", "Black Rook": "r", "Black Queen": "q",
    "Black King": "k",
}


def assign_pieces_to_squares(points, ptsT, ptsL, classes):
    """Snaps each (point, class) detection to its nearest of the 64 square
    centers derived from ptsT/ptsL, and returns a 64-entry FEN-piece list
    (row-major, rank 8 first). First detection to claim a square wins;
    later ones on the same square are dropped. Detections of a class not in
    CLASS_ID_TO_FEN_PIECE (e.g. class 0, "bishop" with no color, present in
    datasets/piecies/data.yaml but with no FEN letter to map to) are skipped
    rather than raising KeyError — see git history for the previous
    behavior and CLAUDE.md's "Class-index mapping" section.
    """
    square_list_centers = []
    for t in range(len(ptsT) - 2, -1, -1):
        for l in range(0, len(ptsT) - 1):
            square_list_centers.append([
                ptsT[t][0] + (ptsT[1][0] / 2),
                ptsL[l][1] + (ptsL[1][1] / 2),
            ])

    cells = spatial.KDTree(square_list_centers)
    chessboard_list = [""] * 64

    for index, point in enumerate(points):
        piece = CLASS_ID_TO_FEN_PIECE.get(classes[index].item())
        if piece is None:
            continue
        _, cell_index = cells.query([point[0], point[1]])
        if len(chessboard_list[cell_index]) < 1:
            chessboard_list[cell_index] = piece

    return chessboard_list


def create_fen(chessboard_list, turn):
    chessboard_matrix = np.array(chessboard_list).reshape(-1, 8)
    fen = ""

    for line in range(8):
        count = 0
        line_str = ""
        for cell in range(8):
            if len(chessboard_matrix[line][cell]) < 1:
                count += 1
            else:
                if count > 0:
                    line_str += str(count)
                    count = 0
                line_str += chessboard_matrix[line][cell]
        if count > 0:
            line_str += str(count)

        fen += line_str
        if line < 7:
            fen += "/"

    return fen + " " + turn + " KQkq - 0 1"


def board_matrix_from_fen(fen):
    """Returns (8x8 matrix, turn). A fresh matrix is built on every call —
    an earlier version of this function (see git history) mutated a single
    module-level matrix in place and only overwrote occupied cells, so a
    square that went from occupied to empty between two calls kept its
    stale value. Fixed here; see
    tests/unit/test_editing.py::test_get_chessboard_matrix_from_fen_does_not_leak_state_between_calls.
    """
    singleline = fen.split("/")
    turn = singleline[7].split(" ")[1]
    singleline[7] = singleline[7].split(" ")[0]

    formatted_fen = ""
    for line in singleline:
        for ch in line:
            if ch.isnumeric():
                formatted_fen += "e" * int(ch)
            else:
                formatted_fen += ch
        formatted_fen += "/"

    board_matrix = np.array([""] * 64).reshape(-1, 8)
    for row_index, row in enumerate(formatted_fen.split("/")[:8]):
        for col_index, ch in enumerate(row):
            if ch != "e":
                board_matrix[row_index][col_index] = ch

    return board_matrix, turn


def edit_chessboard(chessboard, moves_string):
    moves = moves_string.split(";")
    for move in moves:
        square, piece_name = move.split(":")
        row = RANK_TO_ROW[int(square[1])] - 1
        col = COLUMN_INDEX[square[0]]
        chessboard[row][col] = "" if piece_name == "Empty" else EDIT_PIECE_CODES[piece_name]
    return chessboard
