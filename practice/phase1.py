# todo 
# complete piece classes
# score system
# check/checkmate
# game end
# special moves (en passant, castling)
# timer
# github
# GUI
# done.


###############  board representation ##################################

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




############### helper function exercise #######################################
# chess notation to list index
def convert_move(str_coord):
    str_coord = str_coord.strip().lower()

    # if str_coord = e1:

    # takes e and uses the ord function to change it into a number(a = 96, b = 97, c = 98, etc) 
    # then subtracts ord('a') which is 96 to get the correct row number for list indexes (a = 0, b = 1, c = 2, etc)
    col = ord(str_coord[0].lower()) - ord('a')

    # takes the second char of the coordinates and turns it into a string, subtracting 
    # that from 8 to get the chess board coordinate that corresponds to the list index
    row = 8 - int(str_coord[1])

    if not (0 <= row < 8 and 0 <= col < 8):
       raise ValueError(f"Invalid board coordinate: {str_coord}")

    return (row, col)


def validate_player_move(player, piece):
    if player == "white" and piece == piece.upper():
        return True
    
    if player == "black" and piece == piece.lower():
        return True
    
    return False


# list index to chess notation
def convert_to_chess_notation(row, col):

    file = chr(col + ord('a'))
    rank = str(8 - row)

    return file + rank



############### rules engine exercise #########################################

def is_valid(move):
    if len(move) != 2:
        return False
    
    move_file, move_rank = move[0].lower(), move[1]
    if move_file not in 'abcdefgh' or move_rank not in '12345678':
        return False
    return True

# def is_enemy(player, target):
#     if target == "-":
#         return False

#     return (
#         (player == "white" and target.islower()) or
#         (player == "black" and target.isupper())
#     )




############# PIECE CLASSES #################################################

class Piece:
    def __init__(self, symbol, player):
        self.symbol = symbol
        self.player = player


class Queen(Piece):
    def get_moves(self, row, col, board):
        self.valid_moves = []

        self.directions = [
        (-1, 0),   # up
        (1, 0),    # down
        (0, -1),   # left
        (0, 1),    # right
        (-1, -1),  # up-left
        (-1, 1),   # up-right
        (1, -1),   # down-left
        (1, 1)     # down-right
        ]

        for dr, dc in self.directions:
            current_row = row + dr
            current_col = col + dc

            while 0 <= current_row < 8 and 0 <= current_col < 8:
                target = board[current_row][current_col]

                    #empty target square
                if target == "-":
                    self.valid_moves.append((current_row, current_col))


                    #enemy target piece
                elif player == "white" and target.islower():
                    self.valid_moves.append((current_row, current_col))
                    break

                elif player == "black" and target.isupper():
                    self.valid_moves.append((current_row, current_col))
                    break

                    #friendly target piece
                else:
                    break

                current_row += dr
                current_col += dc

        return self.valid_moves

class Pawn(Piece):
    def get_moves(self, row, col, board):
        self.valid_moves = []

        # white pawn
        if self.player == "white":
            # one square forward
            if row - 1 >= 0 and board[row - 1][col] == "-":
                self.valid_moves.append((row - 1, col))

                # first move two squares
                if row == 6 and board[row - 2][col] == "-":
                    self.valid_moves.append((row - 2, col))

            # diagonal captures
            for dc in [-1, 1]:
                new_col = col + dc

                if 0 <= new_col < 8 and row - 1 >= 0:
                    target = board[row - 1][new_col]

                    if target != "-" and target.islower():
                        self.valid_moves.append((row - 1, new_col))

        # black pawn
        else:
            # one square forward
            if row + 1 < 8 and board[row + 1][col] == "-":
                self.valid_moves.append((row + 1, col))

                # first move two squares
                if row == 1 and board[row + 2][col] == "-":
                    self.valid_moves.append((row + 2, col))

            # diagonal captures
            for dc in [-1, 1]:
                new_col = col + dc

                if 0 <= new_col < 8 and row + 1 < 8:
                    target = board[row + 1][new_col]

                    if target != "-" and target.isupper():
                        self.valid_moves.append((row + 1, new_col))

        
        return self.valid_moves


class King(Piece):
    def get_moves(self, row, col, board):
        self.valid_moves = []
        self.directions = [
            (-1, 0),   # up
            (1, 0),    # down
            (0, -1),   # left
            (0, 1),    # right
            (-1, -1),  # up-left
            (-1, 1),   # up-right
            (1, -1),   # down-left
            (1, 1)     # down-right
        ]

        for dr, dc in self.directions:
            current_row = row + dr
            current_col = col + dc

            if 0 <= current_row < 8 and 0 <= current_col < 8:

                target = board[current_row][current_col]


                # empty target square
                if target == "-":
                    self.valid_moves.append((current_row, current_col))

                elif player == "white" and target.islower():
                    self.valid_moves.append((current_row, current_col))

                elif player == "black" and target.isupper():
                    self.valid_moves.append((current_row, current_col))

        return self.valid_moves

class Knight(Piece):
    def get_moves(self, row, col, board):
        self.valid_moves = []

        self.directions = [
            (-2, -1),
            (-2,  1),

            (-1, -2),
            (-1,  2),

            (1, -2),
            (1,  2),

            (2, -1),
            (2,  1)
        ]

        for dr, dc in self.directions:

            current_row = row + dr
            current_col = col + dc

            if 0 <= current_row < 8 and 0 <= current_col < 8:
                target = board[current_row][current_col]

                #empty target square
                if target == "-":
                    self.valid_moves.append((current_row, current_col))

                # enemy target square
                elif player == "white" and target.islower():
                    self.valid_moves.append((current_row, current_col))

                elif player == "black" and target.isupper():
                    self.valid_moves.append((current_row, current_col))

                # friendly pieces = do nothing
        
        return self.valid_moves



class Rook(Piece):
    def get_moves(self, row, col, board):
        self.valid_moves = []

        self.directions = [
            (-1, 0),   # up
            (1, 0),    # down
            (0, -1),   # left
            (0, 1),    # right
        ]

        for dr, dc in self.directions:

            current_row = row + dr
            current_col = col + dc

            while 0 <= current_row < 8 and 0 <= current_col < 8:
                target = board[current_row][current_col]

                #empty target square
                if target == "-":
                    self.valid_moves.append((current_row, current_col))


                #enemy target piece
                elif player == "white" and target.islower():
                    self.valid_moves.append((current_row, current_col))
                    break

                elif player == "black" and target.isupper():
                    self.valid_moves.append((current_row, current_col))
                    break

                #friendly target piece
                else:
                    break

                current_row += dr
                current_col += dc
        
        return self.valid_moves


class Bishop(Piece):
    def get_moves(self, row, col, board):
        self.valid_moves = []

        self.directions = [
            (-1, -1),  # up-left
            (-1, 1),   # up-right
            (1, -1),   # down-left
            (1, 1)     # down-right
        ]

        for dr, dc in self.directions:
            current_row = row + dr
            current_col = col + dc

            while 0 <= current_row < 8 and 0 <= current_col < 8:
                target = board[current_row][current_col]

                # empty target square
                if target == "-":
                    self.valid_moves.append((current_row, current_col))

                # enemy target piece
                elif player == "white" and target.islower():
                    self.valid_moves.append((current_row, current_col))
                    break

                elif player == "black" and target.isupper():
                    self.valid_moves.append((current_row, current_col))
                    break


                # friendly target piece
                else:
                    break

                current_row += dr
                current_col += dc

        return self.valid_moves

    


############# LIST MOVES ####################################################

def list_moves(piece, row, col, player, board):
    valid_moves = []


    # king movement
    if piece.lower() == "k":
        king_piece = King(piece, player)
        valid_moves = king_piece.get_moves(row, col, board)


    # queen movement
    if piece.lower() == "q":
        queen_piece = Queen(piece, player)
        valid_moves = queen_piece.get_moves(row, col, board)


    # bishop movement
    if piece.lower() == "b":
        bishop_piece = Bishop(piece, player)
        valid_moves = bishop_piece.get_moves(row, col, board)
   

    # Rook movement
    if piece.lower() == "r":
        rook_piece = Rook(piece, player)
        valid_moves = rook_piece.get_moves(row, col, board)
   

    # knight movement
    if piece.lower() == "n":
        knight_piece = Knight(piece, player)
        valid_moves = knight_piece.get_moves(row, col, board)


    # pawn movement
    if piece.lower() == "p":
        pawn_piece = Pawn(piece, player)
        valid_moves = pawn_piece.get_moves(row, col, board)


    #print possible moves as chess coordinates
    print("\nPossible moves:")

    for r, c in valid_moves:

        square = convert_to_chess_notation(r, c)

        target_piece = board[r][c]


        #print enemy piece capture possibility in list
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

        #print normal move in list
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
        self.legal_moves = []

    def switch_turn(self):
        # switch to other player
        self.current_p = "black" if self.current_p == "white" else "white" 
        self.turn_count += 1

    def get_current_player(self):
        return self.current_p
    
    
    def validate_from(self, from_pos):

        # ensure move is valid
        while not is_valid(from_pos):
            print("invalid coordinate\n")
            from_pos = input("please select a different piece to move: ")
                

        # get piece
        row1, col1 = convert_move(from_pos)

        selected_piece = self.board[row1][col1]

        # make sure player selection is not an empty square
        while True:
            row1, col1 = convert_move(from_pos)
            selected_piece = self.board[row1][col1]

            if selected_piece != "-":
                break

            print("no piece at selected square\n")
            from_pos = input("please select a different piece to move: ")


        # make sure that player owns the piece they want to move
        while not validate_player_move(self.current_p, selected_piece):

            print("that piece does not belong to you\n")
            from_pos = input("please select a different piece to move: ")

            row1, col1 = convert_move(from_pos)
            selected_piece = self.board[row1][col1]
            

        # get all legal moves for selected piece on board
        self.legal_moves = list_moves(selected_piece, row1, col1, self.current_p, self.board)

        # if piece has no legal moves, prompt again
        while len(self.legal_moves) == 0:

            print("that piece has no legal moves\n")
            from_pos = input("please select a different piece to move: ")

            row1, col1 = convert_move(from_pos)
            selected_piece = self.board[row1][col1]

            self.legal_moves = list_moves(selected_piece, row1, col1, self.current_p, self.board)


        # show all legal moves on board
        highlight_moves(self.board, self.legal_moves)

        # print board
        print_board(self.board, self.current_p)

        return from_pos


    def validate_to(self, to_pos):

        while not is_valid(to_pos):
            print("invalid destination\n")
            to_pos = input("please select a different place to move to: ")

        while True:    
            row2, col2 = convert_move(to_pos)

            if (row2, col2) in self.legal_moves:
                return to_pos
            else:
                print("illegal move for that piece\n")
                to_pos = input("please select a different place to move to: ")

    
    def make_move(self, from_pos, to_pos):
        # simulate move, then switch turns

        row1, col1 = convert_move(from_pos)
        row2, col2 = convert_move(to_pos)

        if not (0 <= row1 < 8 and 0 <= col1 < 8):
            print("invalid FROM position")
            return

        if not (0 <= row2 < 8 and 0 <= col2 < 8):
            print("invalid TO position")
            return

        self.board[row2][col2] = self.board[row1][col1] 
        self.board[row1][col1] = "-"

        print(f"{self.current_p} moves from {from_pos} to {to_pos}")
        self.switch_turn()
        clear_highlights(self.board)


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

# get info of players of next chess game:

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

    # get piece to move from current player and validate move
    from_piece = input("what piece do you want to move?: ")
    from_piece = chess_game.validate_from(from_piece)


    # prompt player to pick where to move piece and validate move
    to_piece = input("where should the piece go?: ")
    to_piece = chess_game.validate_to(to_piece)

    # if move is valid, make move and prepare board for next players move
    chess_game.make_move(from_piece, to_piece)
