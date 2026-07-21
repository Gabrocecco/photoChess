"""Stockfish analysis and SVG board rendering for AnalyzeActivity. Android-
only — nothing on the desktop side needs engine analysis or board images.

Faithful port of the old Android pipeline.py's getbestmove/getboard/geteval
(see git history). Not covered by tests/golden or tests/unit: both require
a live call to stockfish.online, which isn't exercised in this refactor's
test suite. The commented-out berserk/Lichess code path in the original
(dead — always bypassed in favor of the stockfish.online call below) was
dropped rather than carried over, and with it the committed Lichess
API_TOKEN it referenced; see CLAUDE.md "Known rough edges" for the
token-revocation follow-up this doesn't replace.

NOTE: getbestmove() below preserves an existing quirk rather than fixing it
mid-refactor (see CLAUDE.md's Fase 5 note) — response["data"] is read
before response["success"] is checked, so a failed request with no "data"
key raises KeyError instead of returning "Error" like a successful-but-empty
one does.
"""
import json

import chess
import chess.svg
import requests

BOARD_COLORS = {"square dark": "#6A6F7A", "square light": "#D5DEF5", "outer border": "#15781B80"}
ARROW_COLOR = "#77FF61"


def getboard(fen):
    board = chess.Board(fen)
    return chess.svg.board(board, colors=BOARD_COLORS)


def getbestmove(fen):
    print(fen)

    url = "https://stockfish.online/api/stockfish.php?fen=" + fen + "&depth=10&mode=lines"
    response = requests.post(url)

    board = chess.Board(fen)
    data = json.loads(response.text)
    single_moves = data["data"].split(" ")

    if data["success"] == True and len(data["data"]) > 1:
        moved_svgs = []
        for i in range(len(single_moves)):
            from_sq = single_moves[i][0:2]
            to_sq = single_moves[i][2:4]
            if i > 0:
                board.push(chess.Move.from_uci(single_moves[i - 1]))
            arrow = chess.svg.Arrow(
                getattr(chess, from_sq.capitalize()), getattr(chess, to_sq.capitalize()), color=ARROW_COLOR
            )
            moved_svgs.append(str(chess.svg.board(board, colors=BOARD_COLORS, arrows=[arrow])))
        return moved_svgs

    return "Error"


def geteval(fen):
    url = "https://stockfish.online/api/stockfish.php?fen=" + fen + "&depth=10&mode=eval"
    response = requests.post(url)
    data = json.loads(response.text)

    if data["success"] == True and len(data["data"]) > 1:
        return data["data"].split(" ")[2]
    return "Error"
