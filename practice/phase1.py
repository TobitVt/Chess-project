# todo 
# create piece classes
# score system
# check/checkmate
# game end
# special moves (en passant)
# timer
# github
# GUI
# done.


###############  board representation exercise ##################################

# print function:
def print_board(board, current_player):
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
    print(f"player at turn: {current_player}")
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


############### helper function exercise #######################################
# chess notation to list index
def convert_move(str_coord):

    # if str_coord = e1:

    # takes e and uses the ord function to change it into a number(a = 96, b = 97, c = 98, etc) 
    # then subtracts ord('a') which is 96 to get the correct row number for list indexes (a = 0, b = 1, c = 2, etc)
    col = ord(str_coord[0].lower()) - ord('a')

    # takes the second char of the coordinates and turns it into a string, subtracting 
    # that from 8 to get the chess board coordinate that corresponds to the list index
    row = 8 - int(str_coord[1])

    return (row, col)


def validate_player_move(player, piece):
    if player == "white" and piece == piece.upper():
        return True
    
    if player == "black" and piece == piece.lower():
        return True
    
    return False


############### rules engine exercise #########################################

def is_valid(start, end):
    # checks input coordinates are correct length e.g. e4
    if len(start) != 2 or len(end) != 2:
        return False
    

    start_file, start_rank = start[0].lower(), start[1]
    end_file, end_rank = end[0].lower(), end[1]
    
    # Check files (a-h) and ranks (1-8)
    if start_file not in 'abcdefgh' or not start_rank.isdigit() or int(start_rank) < 1 or int(start_rank) > 8:
        return False
    if end_file not in 'abcdefgh' or not end_rank.isdigit() or int(end_rank) < 1 or int(end_rank) > 8:
        return False
    
    return True


############# Exercise 2: Highlight and List Possible Moves #######################

# create classes for pieces

############# PIECE CLASSES #################################################

class Piece:
    def __init__(self, symbol, player):
        self.symbol = symbol
        self.player = player


class Queen(Piece):
    pass

class Pawn(Piece):
    pass

class King(Piece):
    pass

class Knight(Piece):
    pass

class Rook(Piece):
    pass

class Bishop(Piece):
    pass


############# MOVE HELPERS ##################################################
# list index to chess notation
def convert_to_chess_notation(row, col):

    file = chr(col + ord('a'))
    rank = str(8 - row)

    return file + rank


def clear_highlights(board):

    for r in range(8):
        for c in range(8):
            if board[r][c] == "#":
                board[r][c] = "-"

def highlight_moves(board, valid_moves):

    # clear previous highlights first
    clear_highlights(board)

    # add new highlights
    for r, c in valid_moves:

        if board[r][c] == "-":
            board[r][c] = "#"


############# LIST MOVES ####################################################

def list_moves(piece, row, col, player, board):


    valid_moves = []

    #########################################################
    # king MOVEMENT
    #########################################################

    if piece.lower() == "k":

        directions = [
            (-1, 0),   # up
            (1, 0),    # down
            (0, -1),   # left
            (0, 1),    # right
            (-1, -1),  # up-left
            (-1, 1),   # up-right
            (1, -1),   # down-left
            (1, 1)     # down-right
        ]

        for dr, dc in directions:

            current_row = row + dr
            current_col = col + dc

            if 0 <= current_row < 8 and 0 <= current_col < 8:

                target = board[current_row][current_col]

                #################################################
                # EMPTY SQUARE
                #################################################

                if target == "-":
                    valid_moves.append((current_row, current_col))

                elif player == "white" and target.islower():
                    valid_moves.append((current_row, current_col))

                elif player == "black" and target.isupper():
                    valid_moves.append((current_row, current_col))

# friendly pieces = do nothing

    #########################################################
    # QUEEN MOVEMENT
    #########################################################

    if piece.lower() == "q":

        directions = [
            (-1, 0),   # up
            (1, 0),    # down
            (0, -1),   # left
            (0, 1),    # right
            (-1, -1),  # up-left
            (-1, 1),   # up-right
            (1, -1),   # down-left
            (1, 1)     # down-right
        ]

        for dr, dc in directions:

            current_row = row + dr
            current_col = col + dc

            while 0 <= current_row < 8 and 0 <= current_col < 8:

                target = board[current_row][current_col]

                #################################################
                # EMPTY SQUARE
                #################################################

                if target == "-":

                    valid_moves.append((current_row, current_col))

                #################################################
                # ENEMY PIECE
                #################################################

                elif player == "white" and target.islower():

                    valid_moves.append((current_row, current_col))
                    break

                elif player == "black" and target.isupper():

                    valid_moves.append((current_row, current_col))
                    break

                #################################################
                # FRIENDLY PIECE
                #################################################

                else:
                    break

                current_row += dr
                current_col += dc

    #########################################################
    # BISHOP MOVEMENT
    #########################################################

    if piece.lower() == "b":

        directions = [
            (-1, -1),  # up-left
            (-1, 1),   # up-right
            (1, -1),   # down-left
            (1, 1)     # down-right
        ]

        for dr, dc in directions:

            current_row = row + dr
            current_col = col + dc

            while 0 <= current_row < 8 and 0 <= current_col < 8:

                target = board[current_row][current_col]

                #################################################
                # EMPTY SQUARE
                #################################################

                if target == "-":

                    valid_moves.append((current_row, current_col))

                #################################################
                # ENEMY PIECE
                #################################################

                elif player == "white" and target.islower():

                    valid_moves.append((current_row, current_col))
                    break

                elif player == "black" and target.isupper():

                    valid_moves.append((current_row, current_col))
                    break

                #################################################
                # FRIENDLY PIECE
                #################################################

                else:
                    break

                current_row += dr
                current_col += dc

    
    #########################################################
    # Rook MOVEMENT
    #########################################################

    if piece.lower() == "r":

        directions = [
            (-1, 0),   # up
            (1, 0),    # down
            (0, -1),   # left
            (0, 1),    # right
        ]

        for dr, dc in directions:

            current_row = row + dr
            current_col = col + dc

            while 0 <= current_row < 8 and 0 <= current_col < 8:

                target = board[current_row][current_col]

                #################################################
                # EMPTY SQUARE
                #################################################

                if target == "-":

                    valid_moves.append((current_row, current_col))

                #################################################
                # ENEMY PIECE
                #################################################

                elif player == "white" and target.islower():

                    valid_moves.append((current_row, current_col))
                    break

                elif player == "black" and target.isupper():

                    valid_moves.append((current_row, current_col))
                    break

                #################################################
                # FRIENDLY PIECE
                #################################################

                else:
                    break

                current_row += dr
                current_col += dc

   
    #########################################################
    # knight MOVEMENT
    #########################################################

    if piece.lower() == "n":

        directions = [
            (-2, -1),
            (-2,  1),

            (-1, -2),
            (-1,  2),

            (1, -2),
            (1,  2),

            (2, -1),
            (2,  1)
        ]

        for dr, dc in directions:

            current_row = row + dr
            current_col = col + dc

            if 0 <= current_row < 8 and 0 <= current_col < 8:

                target = board[current_row][current_col]

                #################################################
                # EMPTY SQUARE
                #################################################

                if target == "-":
                    valid_moves.append((current_row, current_col))

                elif player == "white" and target.islower():
                    valid_moves.append((current_row, current_col))

                elif player == "black" and target.isupper():
                    valid_moves.append((current_row, current_col))

                # friendly pieces = do nothing


    #########################################################
    # PAWN MOVEMENT
    #########################################################

    elif piece.lower() == "p":

        #################################################
        # WHITE PAWN
        #################################################

        if player == "white":

            # one square forward
            if row - 1 >= 0 and board[row - 1][col] == "-":
                valid_moves.append((row - 1, col))

                # first move two squares
                if row == 6 and board[row - 2][col] == "-":
                    valid_moves.append((row - 2, col))

            # diagonal captures
            for dc in [-1, 1]:

                new_col = col + dc

                if 0 <= new_col < 8 and row - 1 >= 0:

                    target = board[row - 1][new_col]

                    if target != "-" and target.islower():
                        valid_moves.append((row - 1, new_col))

        #################################################
        # BLACK PAWN
        #################################################

        else:

            # one square forward
            if row + 1 < 8 and board[row + 1][col] == "-":
                valid_moves.append((row + 1, col))

                # first move two squares
                if row == 1 and board[row + 2][col] == "-":
                    valid_moves.append((row + 2, col))

            # diagonal captures
            for dc in [-1, 1]:

                new_col = col + dc

                if 0 <= new_col < 8 and row + 1 < 8:

                    target = board[row + 1][new_col]

                    if target != "-" and target.isupper():
                        valid_moves.append((row + 1, new_col))

    #########################################################
    # PRINT MOVES AS CHESS COORDINATES
    #########################################################
    print("\nPossible moves:")

    for r, c in valid_moves:

        square = convert_to_chess_notation(r, c)

        target_piece = board[r][c]

        #################################################
        # ENEMY PIECE CAPTURE
        #################################################

        if target_piece != "-":

            piece_names = {
                "p": "pawn",
                "r": "rook",
                "n": "knight",
                "b": "bishop",
                "q": "queen",
                "k": "king"
            }

            enemy_name = piece_names[target_piece.lower()]

            print(f"{square}(take enemy {enemy_name})", end=" ")

        #################################################
        # NORMAL MOVE
        #################################################

        else:
            print(square, end=" ")

    print("\n")
    return valid_moves


###############  game controller exercise ########################################

class Game:
    def __init__(self, u_board):
        self.board = u_board
        self.current_p = "white"
        self.turn_count = 0

    def switch_turn(self):
        # switch to other player
        self.current_p = "black" if self.current_p == "white" else "white" 
        self.turn_count += 1

    def get_current_player(self):
        return self.current_p
    
    def make_move(self, from_pos, to_pos):
        # simulate move, then switch turns

        # Move logic would go here (validate, update board, etc.)

        row1, col1 = convert_move(from_pos)
        row2, col2 = convert_move(to_pos)

        f = chess_board[row1][col1] 

        if f == "-":
            print("coordinates selected does not contain a piece\n")
            m1 = input("please select a piece to move: ")
            m2 = input("where should the piece be moved?: ")
            self.make_move(m1, m2)
            

        # ensure that player at turn only moves own pieces
        # white: capital letters, black: small letters
        if validate_player_move(self.current_p, f):
            chess_board[row2][col2] = chess_board[row1][col1] 
            chess_board[row1][col1] = "-"
        else:
            print("piece selected does not belong to player at turn\n")
            move1 = input("please select another piece to move: ")
            move2 = input("where should the piece be moved?: ")
            self.make_move(move1, move2)


        print(f"{self.current_p} moves from {from_pos} to {to_pos}")
        self.switch_turn()


#################player representation exercise ###############################
class Player:
    def __init__(self, name, score = 0):
        self.name = name
        self.score = score

    def update_score(self, n):
        self.score += int(n)

    def get_player_info(self):
        return f"{self.name} - {self.score} points"

 

###############  game code: ####################################################

# name1 = input("please enter player 1's name: ")
# score1 = int(input("please enter the elo score of player 1: "))

# player1 = Player(name1, score1)

# name2 = input("please enter player 2's name: ")
# score2 = int(input("please enter the elo score of player 2: "))

# player2 = Player(name2, score2)

player = Player("Alice", 100)
player.update_score(10)  # Add 10
print(player.get_player_info())  # Alice - 110 points

player.update_score(-5)  # Subtract 5
print(player.get_player_info())  # Alice - 105 points

# timeLimit = 60* (int(input("Please select the time limit for each player(5/10/20/30)min: ")))

# timers = {
#     "p1": timeLimit,
#     "p2": timeLimit
# }


chess_game = Game(chess_board)


while True:

    clear_highlights(chess_board)

    print_board(chess_board, chess_game.get_current_player())

    ########################################################
    # SELECT PIECE
    ########################################################

    from_piece = input("what piece do you want to move?: ")

    ########################################################
    # BASIC INPUT VALIDATION
    ########################################################

    if not is_valid(from_piece, from_piece):
        print("invalid coordinate\n")
        continue

    ########################################################
    # GET PIECE
    ########################################################

    row1, col1 = convert_move(from_piece)

    selected_piece = chess_board[row1][col1]

    ########################################################
    # EMPTY SQUARE CHECK
    ########################################################

    if selected_piece == "-":
        print("no piece at selected square\n")
        continue

    ########################################################
    # PLAYER OWNERSHIP CHECK
    ########################################################

    if not validate_player_move(
        chess_game.get_current_player(),
        selected_piece
    ):
        print("that piece does not belong to you\n")
        continue

    ########################################################
    # GENERATE LEGAL MOVES
    ########################################################

    legal_moves = list_moves(
        selected_piece,
        row1,
        col1,
        chess_game.get_current_player(),
        chess_board
    )

    ########################################################
    # HIGHLIGHT MOVES
    ########################################################

    highlight_moves(chess_board, legal_moves)

    ########################################################
    # SHOW BOARD
    ########################################################

    print_board(chess_board, chess_game.get_current_player())

    ########################################################
    # NO LEGAL MOVES
    ########################################################

    if len(legal_moves) == 0:
        print("that piece has no legal moves\n")
        continue

    ########################################################
    # CHOOSE DESTINATION
    ########################################################

    to_piece = input("where should the piece go?: ")

    ########################################################
    # VALIDATE DESTINATION
    ########################################################

    if not is_valid(to_piece, to_piece):
        print("invalid destination\n")
        continue

    row2, col2 = convert_move(to_piece)

    ########################################################
    # CHECK LEGALITY
    ########################################################

    if (row2, col2) not in legal_moves:
        print("illegal move for that piece\n")
        continue

    ########################################################
    # MAKE MOVE
    ########################################################

    chess_game.make_move(from_piece, to_piece)

    clear_highlights(chess_board)

    print_board(chess_board, chess_game.get_current_player())

    ########################################################
    # EXIT
    ########################################################

    # cont = input("type quit to exit or press enter to continue: ")

    # if cont.lower() == "quit":
    #     break