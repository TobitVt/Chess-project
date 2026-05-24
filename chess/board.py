###############  board representation ##################################

# print function:
def print_board(board):
    print("\n   a b c d e f g h \n")  
    for i in range(8):
        row_str = " ".join(board[i])
        if i == 0:
            print(f"{8 - i}  {row_str}  - Black side")
        elif i == 7:
            print(f"{8 - i}  {row_str}  - White side")
        else:
            print(f"{8 - i}  {row_str}")
    
    print("\n   a b c d e f g h \n")
    # print(f"player at turn: {current_player}")
    # print("Board orientation: White at bottom (ranks 1-8), Black at top (ranks 8-1)")



# create chess board using list comprehension
chess_board = [["-" for i in range(8)] for j in range(8)]

# create list of pieces in order
pieces = ["r", "n", "b", "q", "k", "b", "n", "r"]

# place pieces for white

for i in range(8):
    chess_board[0][i] = pieces[i]  # Lowercase for Black
    chess_board[1][i] = "p"


# place pieces for black

for i in range(8):
    chess_board[7][i] = pieces[i].upper() # Uppercase for White
    chess_board[6][i] = "P"



def clear_highlights(board):

    for r in range(8):
        for c in range(8):
            if board[r][c] == "#":
                board[r][c] = "-"

def highlight_moves(board, valid_moves):

    # clear previous highlights first
    # clear_highlights(board)

    # add new highlights
    for r, c in valid_moves:

        if board[r][c] == "-":
            board[r][c] = "#"

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

def print_possible_moves(valid_moves, board):
    print("\nPossible moves:")

    for r, c in valid_moves:

        square = convert_to_chess_notation(r, c)
        target_piece = board[r][c]

        if target_piece != "-":
            enemy_name = piece_names[target_piece.lower()]
            print(f"{square}(take enemy {enemy_name})", end=" ")

        else:
            print(square, end=" ")

    print("\n")

