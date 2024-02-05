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
    svg = chess.svg.board(board)
    return svg

def getmoveboard(fen, fromString, toString):
    board = chess.Board(fen)
    svg = chess.svg.board(board, arrows=[chess.svg.Arrow(getattr(chess, fromString.capitalize()), getattr(chess, toString.capitalize()), color="#FF0000")])
    return svg