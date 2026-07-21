"""Stockfish analysis and SVG board rendering for AnalyzeActivity. Android-
only — nothing on the desktop side needs engine analysis or board images.

getboard() is a faithful port of the old Android pipeline.py's getboard()
(see git history). getbestmove()/geteval() are a rewrite, not a port: the
v1 endpoint they used to call (stockfish.online/api/stockfish.php) has been
deprecated by the provider — confirmed live, {"success":false,"data":"This
endpoint (v1) is no longer available. Please switch to using API v2."} —
so best-move/eval were already broken before this refactor touched
anything. This is a genuine behavior change (a dead feature restored with
new logic against v2, api/s/v2.php), not a preserved one; see CLAUDE.md's
Fase 5 note. v2 requires GET (a v1-style POST gets a 403), caps depth < 16,
and returns a different shape: {success, evaluation, mate, bestmove,
continuation} instead of v1's {success, data}. "continuation" (a
space-separated UCI move list) plays the same role v1's "data" did for
getbestmove's move-by-move SVG loop.

The commented-out berserk/Lichess code path in the pre-refactor original
(dead — always bypassed) was dropped rather than carried over, and with it
the committed Lichess API_TOKEN it referenced; see CLAUDE.md "Known rough
edges" for the token-revocation follow-up this doesn't replace.

Not covered by tests/golden or tests/unit: both would require a live call
to stockfish.online. Manually verified against the live v2 endpoint for a
normal position, a forced mate, and checkmate/stalemate (continuation is
null in that last case) while writing this — which is also how a bug in an
earlier version of geteval() was caught before it shipped: it returned
"M3"-style mate notation, and AnalyzeActivity.analyzeMatch() in
AnalyzeActivity.java unconditionally does
Double.parseDouble(res.toString()) on any non-"Error" result, so that
would have thrown a NumberFormatException on-device on any position with a
forced mate. geteval() now returns a large signed sentinel number for mate
instead (see MATE_SENTINEL_EVALUATION below).
"""
import chess
import chess.svg
import requests

STOCKFISH_API_URL = "https://stockfish.online/api/s/v2.php"
STOCKFISH_DEPTH = 10  # API rejects depth >= 16
REQUEST_TIMEOUT_SECONDS = 10

BOARD_COLORS = {"square dark": "#6A6F7A", "square light": "#D5DEF5", "outer border": "#15781B80"}
ARROW_COLOR = "#77FF61"


def getboard(fen):
    board = chess.Board(fen)
    return chess.svg.board(board, colors=BOARD_COLORS)


def _query_stockfish(fen):
    response = requests.get(
        STOCKFISH_API_URL, params={"fen": fen, "depth": STOCKFISH_DEPTH}, timeout=REQUEST_TIMEOUT_SECONDS
    )
    return response.json()


def getbestmove(fen):
    print(fen)
    try:
        data = _query_stockfish(fen)
    except requests.RequestException:
        return "Error"

    continuation = data.get("continuation") if data.get("success") else None
    if not continuation:
        return "Error"

    single_moves = continuation.split(" ")
    board = chess.Board(fen)
    moved_svgs = []
    for i, move_uci in enumerate(single_moves):
        from_sq = move_uci[0:2]
        to_sq = move_uci[2:4]
        if i > 0:
            board.push(chess.Move.from_uci(single_moves[i - 1]))
        arrow = chess.svg.Arrow(
            getattr(chess, from_sq.capitalize()), getattr(chess, to_sq.capitalize()), color=ARROW_COLOR
        )
        moved_svgs.append(str(chess.svg.board(board, colors=BOARD_COLORS, arrows=[arrow])))
    return moved_svgs


MATE_SENTINEL_EVALUATION = 100.0  # larger than any plausible non-mate centipawn eval


def geteval(fen):
    # AnalyzeActivity.analyzeMatch() unconditionally does
    # Double.parseDouble(res.toString()) on anything that isn't literally
    # "Error", so this must always return a valid decimal string — no "M3"
    # mate notation, which would throw a NumberFormatException on the Java
    # side and was caught by exercising this against the live endpoint.
    try:
        data = _query_stockfish(fen)
    except requests.RequestException:
        return "Error"

    if not data.get("success"):
        return "Error"

    if data.get("mate") is not None:
        mate_in = float(data["mate"])
        signed_sentinel = MATE_SENTINEL_EVALUATION if mate_in >= 0 else -MATE_SENTINEL_EVALUATION
        return str(signed_sentinel)

    evaluation = data.get("evaluation")
    return str(evaluation) if evaluation is not None else "Error"
