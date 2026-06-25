from utils import *

###############  board representation ##################################

def create_board():
    # create chess board using list comprehension
    chess_board = [["-" for i in range(8)] for j in range(8)]

    # create list of pieces in order
    pieces = ["r", "n", "b", "q", "k", "b", "n", "r"]

    # place pieces for black

    for i in range(8):
        chess_board[0][i] = pieces[i]  # Lowercase for Black
        chess_board[1][i] = "p"


    # place pieces for white

    for i in range(8):
        chess_board[7][i] = pieces[i].upper() # Uppercase for White
        chess_board[6][i] = "P"

    return chess_board

piece_values = {
    "p": 1,
    "n": 3,
    "b": 3,
    "r": 5,
    "q": 9,
    "k": 0
}

piece_names = {
        "p": "pawn",
        "r": "rook",
        "n": "knight",
        "b": "bishop",
        "q": "queen",
        "k": "king"
    }

def get_piece_name(piece):
    if piece == "-":
        return None

    color = "black" if piece.islower() else "white"
    name = piece_names[piece.lower()]
    return f"{color} {name}"

