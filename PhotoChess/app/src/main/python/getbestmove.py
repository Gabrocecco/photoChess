import berserk
import chess
import chess.svg

API_TOKEN = "lip_AogrJ6dUu8ruSPMBZNUW"


def getbestmove(fen):
    session = berserk.TokenSession(API_TOKEN)
    client = berserk.Client(session=session)

    analysis = client.analysis.get_cloud_evaluation(fen, 1)
    dict = analysis["pvs"]
    return(dict.pop(0)['moves'].split(' ')[0])

def getboard(fen):
    board = chess.Board(fen)
    svg = chess.svg.board(board, colors={"square dark" : "#6A6F7A", "square light" : "#D5DEF5", "outer border" : "#15781B80"})
    return svg

def getmoveboard(fen, fromString, toString):
    board = chess.Board(fen)
    svg = chess.svg.board(board, colors={"square dark" : "#6A6F7A", "square light" : "#D5DEF5", "outer border" : "#15781B80"}, arrows=[chess.svg.Arrow(getattr(chess, fromString.capitalize()), getattr(chess, toString.capitalize()), color="#77FF61")])
    return svg