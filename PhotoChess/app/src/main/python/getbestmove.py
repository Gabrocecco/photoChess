import berserk
import chess
import chess.svg

API_TOKEN = "lip_AogrJ6dUu8ruSPMBZNUW"


def getbestmove(fen):
    session = berserk.TokenSession(API_TOKEN)
    client = berserk.Client(session=session)

    analysis = client.analysis.get_cloud_evaluation(fen, 1)
    dict = analysis["pvs"]

    singlemoves = dict[0]["moves"].split(" ")
    maxnofmoves = 0
    board = chess.Board(fen)
    movedSvg = []

    if(len(singlemoves) > 5):
        maxnofmoves = 5
    else:
        maxnofmoves = len(singlemoves)

    for i in range(maxnofmoves):
        fromString = singlemoves[i][0:2]
        toString = singlemoves[i][2:4]
        totalmovesSvg = ""

        if i==0:
            svg = chess.svg.board(board, colors={"square dark" : "#6A6F7A", "square light" : "#D5DEF5", "outer border" : "#15781B80"}, arrows=[chess.svg.Arrow(getattr(chess, fromString.capitalize()), getattr(chess, toString.capitalize()), color="#77FF61")])
        else:
            move = chess.Move.from_uci(singlemoves[i-1])
            board.push(move)
            svg = chess.svg.board(board, colors={"square dark" : "#6A6F7A", "square light" : "#D5DEF5", "outer border" : "#15781B80"}, arrows=[chess.svg.Arrow(getattr(chess, fromString.capitalize()), getattr(chess, toString.capitalize()), color="#77FF61")])
        movedSvg.append(str(svg))

    return movedSvg    
    

def getboard(fen):
    board = chess.Board(fen)
    svg = chess.svg.board(board, colors={"square dark" : "#6A6F7A", "square light" : "#D5DEF5", "outer border" : "#15781B80"})
    return svg

def getmoveboard(fen, fromString, toString):
    board = chess.Board(fen)
    svg = chess.svg.board(board, colors={"square dark" : "#6A6F7A", "square light" : "#D5DEF5", "outer border" : "#15781B80"}, arrows=[chess.svg.Arrow(getattr(chess, fromString.capitalize()), getattr(chess, toString.capitalize()), color="#77FF61")])
    return svg

def getfen(bitmapImage, turn):
    #allFunctions
    return "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R " + turn + " KQkq - 1 2"

import numpy as np

dictColumn = {'A':0, 'B': 1, 'C':2, 'D':3, 'E':4, 'F':5, 'G':6, 'H':7}
dictEditPieces = {"Empty":'0', "White Pawn":'P', "White Bishop":'B', "White Knight":'N', 
              "White Rook":'R', "White Queen":'Q', "White King":'K', "Black Pawn":'p',
              "Black Bishop":'b', "Black Knight":'n', "Black Rook":'r', "Black Queen":'q', "Black King":'k'}

dictFenPieces = {
        1:'b', 2:'k', 3:'n', 4:'p', 5:'q', 6:'r', 7:'B', 8:'K', 9:'N', 10:'P', 11:'Q', 12:'R'
    }

dictCell = {1:8, 2:7, 3:6, 4:5, 5:4, 6:3, 7:2, 8:1}





fen = "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 1 2"

chessboard_list = ["","","","","","","","",
            "","","","","","","","",
            "","","","","","","","",
            "","","","","","","","",
            "","","","","","","","",
            "","","","","","","","",
            "","","","","","","","",
            "","","","","","","",""]

arr = np.array(chessboard_list)
chessboard_matrix = arr.reshape(-1, 8)


def getChessboardMatrixfromFen(fen):
    singleline = fen.split("/")
    singleline[7] = singleline[7].split(" ")[0]
    formatted_fen = ""
    for line in singleline:
        for el in range(len(line)):
            if(line[el].isnumeric()):
                for i in range(int(line[el])):
                    formatted_fen = formatted_fen + 'e'
            else:
                formatted_fen = formatted_fen + line[el]
    
        formatted_fen = formatted_fen + "/"
    
    singleformattedline = formatted_fen.split("/")
    index = 0
    for line in singleformattedline:
        for el in range(len(line)):
            if(line[el]!='e'):
                chessboard_matrix[index][el] = line[el]
        index = index + 1
    return chessboard_matrix
    


def editchessboardwmoves(chessboard, movesString):
    moves = movesString.split(";")
    for move in moves:
        parts = move.split(':')
        if(parts[1] == "Empty"):
            chessboard[dictCell[int(parts[0][1])]-1][int(dictColumn[parts[0][0]])] = ""
        else:
            chessboard[dictCell[int(parts[0][1])]-1][int(dictColumn[parts[0][0]])] = dictEditPieces[parts[1]]
    return chessboard

def create_fen(chessboard_matrix):
    fen = ""

    for line in range(8):
        count = 0
        tempString = ""
        for cell in range(8): 
            if(len(chessboard_matrix[line][cell]) < 1):
                count = count + 1
            else:
                if(count > 0):
                    tempString = tempString + str(count)
                    count = 0
                tempString = tempString + chessboard_matrix[line][cell]
        if(count > 0):
            tempString = tempString + str(count)
        
        fen = fen + tempString
        if(line < 7):
            fen = fen + "/"
        
    fen = fen + " w KQkq - 0 1"
    return fen

def getfenfromedits(fen, moves):
    chessboard = getChessboardMatrixfromFen(fen)
    chessboard = editchessboardwmoves(chessboard, moves)
    newfen = create_fen(chessboard)
    return newfen

