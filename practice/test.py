import random
import sqlite3
import json
import hashlib

# todo 
# INTERFACE

# add timer
# done.



############### DATABASE ###############################################
DB_NAME = "chess_game.db"
DEFAULT_ELO = 100

def connect():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        elo INTEGER DEFAULT 0,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        draws INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saved_games (
        save_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id INTEGER NOT NULL,
        board_state TEXT NOT NULL,
        current_turn TEXT NOT NULL,
        bot_difficulty TEXT,
        bot_color TEXT,
        time_limit_seconds INTEGER,
        player_time_left INTEGER,
        saved_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (player_id) REFERENCES players(player_id)
    )
    """)

    cursor.execute("""


    """)

    conn.commit()
    conn.close()


def create_player(u_name, p_word):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO players (username, password) values (?, ?)""", (u_name, p_word))
        conn.commit()
        player_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        conn.close()
        return None
    
    conn.close()
    return player_id


def get_player(u_name):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT player_id, username, password, elo, wins, losses, draws
        FROM players
        WHERE username = ?
        """, (u_name,))

    player = cursor.fetchone()

    conn.close()
    return player


def save_game(player_id, board, current_turn, bot_difficulty, bot_color=None, time_limit_seconds=None, player_time_left=None):
    conn = connect()
    cursor = conn.cursor()

    board_state = json.dumps(board)

    cursor.execute("""
    INSERT INTO saved_games (
        player_id,
        board_state,
        current_turn,
        bot_difficulty,
        bot_color,
        time_limit_seconds,
        player_time_left
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (player_id, board_state, current_turn, bot_difficulty, bot_color, time_limit_seconds, player_time_left))

    conn.commit()
    save_id = cursor.lastrowid

    conn.close()
    return save_id

def get_all_saved_games(player_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT save_id, current_turn, bot_difficulty, saved_at
    FROM saved_games
    WHERE player_id = ?
    ORDER BY saved_at DESC
    """, (player_id,))

    saves = cursor.fetchall()

    conn.close()
    return saves

def load_saved_game(save_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT board_state, current_turn, bot_difficulty, bot_color, time_limit_seconds, player_time_left
    FROM saved_games
    WHERE save_id = ?
    """, (save_id,))

    save = cursor.fetchone()
    conn.close()

    if save is None:
        return None

    board_state, current_turn, bot_difficulty, bot_color, time_limit_seconds, player_time_left = save

    board = json.loads(board_state)


    return {
        "board": board,
        "current_turn": current_turn,
        "bot_difficulty": bot_difficulty,
        "bot_color": bot_color,
        "time_limit_seconds": time_limit_seconds,
        "player_time_left": player_time_left,
    }

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_starting_elo(player_elo):
    return player_elo if player_elo and player_elo > 0 else DEFAULT_ELO


def calculate_expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400.0))


def calculate_elo_change(rating_a, rating_b, actual_score, k_factor=24):
    expected_score = calculate_expected_score(rating_a, rating_b)
    return int(round(k_factor * (actual_score - expected_score)))


def update_player_rating(player_id, new_elo, result):
    conn = connect()
    cursor = conn.cursor()

    if result == "win":
        cursor.execute("UPDATE players SET elo = ?, wins = wins + 1 WHERE player_id = ?", (new_elo, player_id))
    elif result == "draw":
        cursor.execute("UPDATE players SET elo = ?, draws = draws + 1 WHERE player_id = ?", (new_elo, player_id))
    else:
        cursor.execute("UPDATE players SET elo = ?, losses = losses + 1 WHERE player_id = ?", (new_elo, player_id))

    conn.commit()
    conn.close()


def apply_game_result_elo(chess_game, result, human_player, human_player_id):
    if not result or human_player is None or human_player_id is None:
        return None

    human_color = next((color for color, player in chess_game.players.items() if player is human_player), None)
    if human_color is None:
        return None

    opponent_color = "black" if human_color == "white" else "white"
    opponent_player = chess_game.players[opponent_color]

    human_rating = getattr(human_player, "elo", getattr(human_player, "score", DEFAULT_ELO))
    opponent_rating = getattr(opponent_player, "elo", getattr(opponent_player, "score", DEFAULT_ELO))

    if result["outcome"] == "draw":
        actual_score = 0.5
        outcome = "draw"
    else:
        actual_score = 1.0 if result["winner"] == human_color else 0.0
        outcome = "win" if actual_score == 1.0 else "loss"

    new_rating = human_rating + calculate_elo_change(human_rating, opponent_rating, actual_score)
    update_player_rating(human_player_id, new_rating, outcome)
    human_player.update_elo(new_rating)
    print(f"{human_player.name} rating updated to {new_rating} ({outcome}).")
    return new_rating

###############  board representation ##################################

# print function:
def print_board(board, highlights=None):
    if highlights is None:
        highlights = []

    print("\n   a b c d e f g h \n")

    for r in range(8):
        row_items = []

        for c in range(8):
            if (r, c) in highlights:
                if board[r][c] == "-":
                    row_items.append("#")
                else:
                    row_items.append("*")
            else:
                row_items.append(board[r][c])

        row_str = " ".join(row_items)

        if r == 0:
            print(f"{8 - r}  {row_str}  - Black side")
        elif r == 7:
            print(f"{8 - r}  {row_str}  - White side")
        else:
            print(f"{8 - r}  {row_str}")

    print("\n   a b c d e f g h \n")



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
    if piece == "-":
        return False
    
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


#################player representation exercise ###############################
class Player:
    def __init__(self, name, elo = 100, score = 0):
        self.name = name
        self.score = score
        self.elo = elo
        self.captured_pieces = []

    def update_score(self, n):
        self.score += int(n)

    def update_elo(self, new_elo):
        self.elo = new_elo

    def capture_piece(self, piece):
        self.captured_pieces.append(piece)

    def get_captured_list(self):
        return self.captured_pieces

    def get_player_info(self):
        return f"{self.name} - {self.score} points"




############# PIECE CLASSES #################################################

class Piece:
    def __init__(self, symbol, player):
        self.symbol = symbol
        self.player = player

    def is_enemy(self, target):
        if target == "-":
            return False

        return (
            (self.player == "white" and target.islower()) or
            (self.player == "black" and target.isupper())
        )



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
                elif self.is_enemy(target):
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

            forward_row = row - 1
            double_forward_row = row - 2
            start_row = 6

            # one square forward
            if forward_row >= 0 and board[forward_row][col] == "-":
                self.valid_moves.append((forward_row, col))

                # first move two squares
                if row == start_row and board[double_forward_row][col] == "-":
                    self.valid_moves.append((double_forward_row, col))

            # diagonal captures
            for dc in [-1, 1]:
                capture_col = col + dc

                if 0 <= capture_col < 8 and forward_row >= 0:
                    target = board[forward_row][capture_col]

                    if self.is_enemy(target):
                        self.valid_moves.append((forward_row, capture_col))

        # black pawn
        else:

            forward_row = row + 1
            double_forward_row = row + 2
            start_row = 1

            # one square forward
            if forward_row < 8 and board[forward_row][col] == "-":
                self.valid_moves.append((forward_row, col))

                # first move two squares
                if row == start_row and board[double_forward_row][col] == "-":
                    self.valid_moves.append((double_forward_row, col))

            # diagonal captures
            for dc in [-1, 1]:
                capture_col = col + dc

                if 0 <= capture_col < 8 and forward_row < 8:
                    target = board[forward_row][capture_col]

                    if self.is_enemy(target):
                        self.valid_moves.append((forward_row, capture_col))

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

                # friendly square
                if target != "-" and not self.is_enemy(target):
                    continue

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
                elif self.is_enemy(target):
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
                elif self.is_enemy(target):
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
                elif self.is_enemy(target):
                    self.valid_moves.append((current_row, current_col))
                    break


                # friendly target piece
                else:
                    break

                current_row += dr
                current_col += dc

        return self.valid_moves



def create_piece_object(piece_symbol, player):
    piece_classes = {
        "q": Queen,
        "k": King,
        "r": Rook,
        "b": Bishop,
        "n": Knight,
        "p": Pawn
    }

    piece_class = piece_classes.get(piece_symbol.lower())

    if not piece_class:
        return None
    
    return piece_class(piece_symbol, player)


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


###############  game controller exercise ########################################

class Game:
    def __init__(self, u_board, pWhite, pBlack):
        self.board = u_board
        self.current_p = "white"
        self.turn_count = 0
        self.legal_moves = []

        self.players = {
            "white": pWhite,
            "black": pBlack
        }
        
        self.king_moved = {
            "white": False,
            "black": False
        }

        self.rook_moved = {
            "white": {
                "kingside": False,
                "queenside": False
            },
            "black": {
                "kingside": False,
                "queenside": False
            }
        }

        self.en_passant_target = None
        self.en_passant_capture_square = None
        self.en_passant_victim_player = None

    def switch_turn(self):
        # switch to other player
        self.current_p = "black" if self.current_p == "white" else "white" 
        self.turn_count += 1

    def get_current_player(self):
        return self.players[self.current_p]
    
    def is_square_attacked(self, row, col, enemy_player):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]

                if piece == "-":
                    continue

                if not validate_player_move(enemy_player, piece):
                    continue

                # pawns attack diagonally, not forward
                if piece.lower() == "p":

                    if enemy_player == "white":
                        pawn_attacks = [(r - 1, c - 1), (r - 1, c + 1)]
                    else:
                        pawn_attacks = [(r + 1, c - 1), (r + 1, c + 1)]

                    if (row, col) in pawn_attacks:
                        return True

                else:
                    piece_obj = create_piece_object(piece, enemy_player)
                    moves = piece_obj.get_moves(r, c, self.board)

                    if (row, col) in moves:
                        return True

        return False
    
    def find_king(self, player):
        target = "K" if player == "white" else "k"

        for r in range(8):
            for c in range(8):

                if self.board[r][c] == target:
                    return (r, c)

        return None

    def is_in_check(self, player):
        king_pos = self.find_king(player)

        if king_pos is None:
            return False

        king_row, king_col = king_pos

        enemy = "black" if player == "white" else "white"

        return self.is_square_attacked(king_row, king_col, enemy)
        
    def simulate_move(self, row1, col1, row2, col2):
        moving_piece = self.board[row1][col1]

        captured_piece = self.board[row2][col2]
        en_passant_info = None

        if self.is_en_passant_move(moving_piece, row2, col2):
            capture_row, capture_col = self.en_passant_capture_square
            captured_piece = self.board[capture_row][capture_col]

            en_passant_info = (capture_row, capture_col, captured_piece)

            self.board[capture_row][capture_col] = "-"

        self.board[row2][col2] = self.board[row1][col1]
        self.board[row1][col1] = "-"

        return captured_piece, en_passant_info
    
    def undo_move(self, row1, col1, row2, col2, move_info):
        captured_piece, en_passant_info = move_info

        self.board[row1][col1] = self.board[row2][col2]
        self.board[row2][col2] = captured_piece

        if en_passant_info is not None:
            capture_row, capture_col, captured_pawn = en_passant_info

            self.board[row2][col2] = "-"
            self.board[capture_row][capture_col] = captured_pawn


    def is_legal_after_move(self, player, row1, col1, row2, col2):
        move_info = self.simulate_move(row1, col1, row2, col2)

        in_check = self.is_in_check(player)

        self.undo_move(row1, col1, row2, col2, move_info)

        return not in_check
    
        
    def get_legal_moves(self, player, row1, col1, piece_object):

        pseudo_moves = piece_object.get_moves(row1, col1, self.board)

        piece = self.board[row1][col1]

        if piece.lower() == "k":
            pseudo_moves += self.get_castling_moves(player, row1, col1)

        if piece.lower() == "p":
            pseudo_moves += self.get_en_passant_moves(player, row1, col1)

        legal_moves = []

        for row2, col2 in pseudo_moves:
            target_piece = self.board[row2][col2]

            # kings are not captured in chess
            if target_piece != "-" and target_piece.lower() == "k":
                continue

            if self.is_legal_after_move(player, row1, col1, row2, col2):
                legal_moves.append((row2, col2))

        return legal_moves
        
    def has_any_legal_moves(self, player):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]

                if piece == "-":
                    continue

                # ensure piece belongs to player
                if not validate_player_move(player, piece):
                    continue

                piece_obj = create_piece_object(piece, player)
                legal_moves = self.get_legal_moves(player, r, c, piece_obj)

                if len(legal_moves) > 0:
                    return True

        return False
    
    def update_special_move_state(self, moving_piece, row1, col1, row2, col2):

        # update king moved state
        if moving_piece == "K":
            self.king_moved["white"] = True

        elif moving_piece == "k":
            self.king_moved["black"] = True

        # update rook moved state
        if moving_piece == "R":
            if row1 == 7 and col1 == 0:
                self.rook_moved["white"]["queenside"] = True
            elif row1 == 7 and col1 == 7:
                self.rook_moved["white"]["kingside"] = True

        elif moving_piece == "r":
            if row1 == 0 and col1 == 0:
                self.rook_moved["black"]["queenside"] = True
            elif row1 == 0 and col1 == 7:
                self.rook_moved["black"]["kingside"] = True

        # reset en passant by default
        self.en_passant_target = None
        self.en_passant_capture_square = None
        self.en_passant_victim_player = None

        # create en passant opportunity after a pawn moves two squares
        if moving_piece.lower() == "p" and abs(row2 - row1) == 2:
            middle_row = (row1 + row2) // 2

            self.en_passant_target = (middle_row, col1)
            self.en_passant_capture_square = (row2, col2)
            self.en_passant_victim_player = self.current_p
            
    def move_rook_for_castling(self, row1, col1, row2, col2):
        moving_piece = self.board[row2][col2]

        if moving_piece.lower() != "k":
            return

        # castling king must stay on the same row
        if row1 != row2:
            return

        # castling means king moved two columns
        if abs(col2 - col1) != 2:
            return

        # kingside castling
        if col2 == 6:
            self.board[row1][5] = self.board[row1][7]
            self.board[row1][7] = "-"

        # queenside castling
        elif col2 == 2:
            self.board[row1][3] = self.board[row1][0]
            self.board[row1][0] = "-"

    def is_checkmate(self, player):
        return self.is_in_check(player) and not self.has_any_legal_moves(player)
    
    def is_stalemate(self, player):
        return not self.is_in_check(player) and not self.has_any_legal_moves(player)
    
    def get_piece_at_position(self, pos):
        row, col = convert_move(pos)
        return row, col, self.board[row][col]
    
    def get_valid_coordinate(self, prompt, input_func=input):
        pos = input_func(prompt)

        while not is_valid(pos):
            print("invalid coordinate\n")
            pos = input_func(prompt)

        return pos
    
    def validate_from(self, from_pos, input_func=input):
        # ensure move is valid

        while not is_valid(from_pos):
            print("invalid coordinate\n")
            from_pos = self.get_valid_coordinate("please select a valid piece to move: ", input_func)

        # get piece
        row1, col1, selected_piece = self.get_piece_at_position(from_pos)

        # make sure player selection is not an empty square
        while selected_piece == "-":
            print("no piece at selected square\n")
            from_pos = self.get_valid_coordinate("please select a different piece to move: ", input_func)
            row1, col1, selected_piece = self.get_piece_at_position(from_pos)

        # make sure that player owns the piece they want to move
        while not validate_player_move(self.current_p, selected_piece):
            print("that piece does not belong to you\n")
            from_pos = self.get_valid_coordinate("please select a different piece to move: ", input_func)
            row1, col1, selected_piece = self.get_piece_at_position(from_pos)

            while selected_piece == "-":
                print("no piece at selected square\n")
                from_pos = self.get_valid_coordinate("please select a different piece to move: ", input_func)
                row1, col1, selected_piece = self.get_piece_at_position(from_pos)

        # get all legal moves for selected piece on board
        piece_object = create_piece_object(selected_piece, self.current_p)
        self.legal_moves = self.get_legal_moves(self.current_p, row1, col1, piece_object)

        # if piece has no legal moves, prompt again
        while len(self.legal_moves) == 0:
            print("that piece has no legal moves\n")
            from_pos = self.get_valid_coordinate("please select a different piece to move: ", input_func)
            row1, col1, selected_piece = self.get_piece_at_position(from_pos)

            while selected_piece == "-":
                print("no piece at selected square\n")
                from_pos = self.get_valid_coordinate("please select a different piece to move: ", input_func)
                row1, col1, selected_piece = self.get_piece_at_position(from_pos)

            while not validate_player_move(self.current_p, selected_piece):
                print("that piece does not belong to you\n")
                from_pos = self.get_valid_coordinate("please select a different piece to move: ", input_func)
                row1, col1, selected_piece = self.get_piece_at_position(from_pos)

            piece_object = create_piece_object(selected_piece, self.current_p)
            self.legal_moves = self.get_legal_moves(self.current_p, row1, col1, piece_object)

        print_possible_moves(self.legal_moves, self.board)
        print_board(self.board, self.legal_moves)

        return from_pos


    def validate_to(self, to_pos, input_func=input):

        while True:

            while not is_valid(to_pos):
                print("invalid destination\n")
                to_pos = input_func("please select a different place to move to: ")

            row2, col2 = convert_move(to_pos)

            if (row2, col2) in self.legal_moves:
                return to_pos

            print("illegal move for that piece\n")
            to_pos = input_func("please select a different place to move to: ")

    def should_promote_pawn(self, piece, row):

        if piece.lower() != "p":
            return False

        if self.current_p == "white" and row == 0:
            return True

        if self.current_p == "black" and row == 7:
            return True

        return False

    def promote_pawn(self, row, col):

        promotion_options = {
            "q": "queen",
            "r": "rook",
            "b": "bishop",
            "n": "knight"
        }

        choice = input("Promote pawn to queen, rook, bishop, or knight? (q/r/b/n): ").lower()

        while choice not in promotion_options:
            print("invalid promotion choice\n")
            choice = input("Choose q, r, b, or n: ").lower()

        # white pieces are uppercase
        if self.current_p == "white":
            self.board[row][col] = choice.upper()

        # black pieces are lowercase
        else:
            self.board[row][col] = choice

        print(f"Pawn promoted to {promotion_options[choice]}")

    def get_castling_moves(self, player, row, col):
        castling_moves = []

        back_row = 7 if player == "white" else 0
        king_symbol = "K" if player == "white" else "k"
        rook_symbol = "R" if player == "white" else "r"
        enemy = "black" if player == "white" else "white"

        # King must be on original square
        if row != back_row or col != 4:
            return castling_moves

        if self.board[row][col] != king_symbol:
            return castling_moves

        # King must not have moved
        if self.king_moved[player]:
            return castling_moves

        # King may not castle while currently in check
        if self.is_in_check(player):
            return castling_moves

        # kingside castling
        if not self.rook_moved[player]["kingside"]:
            if self.board[back_row][7] == rook_symbol:
                if self.board[back_row][5] == "-" and self.board[back_row][6] == "-":
                    if not self.is_square_attacked(back_row, 5, enemy) and not self.is_square_attacked(back_row, 6, enemy):
                        castling_moves.append((back_row, 6))

        # queenside castling
        if not self.rook_moved[player]["queenside"]:
            if self.board[back_row][0] == rook_symbol:
                if self.board[back_row][1] == "-" and self.board[back_row][2] == "-" and self.board[back_row][3] == "-":
                    if not self.is_square_attacked(back_row, 3, enemy) and not self.is_square_attacked(back_row, 2, enemy):
                        castling_moves.append((back_row, 2))

        return castling_moves
    
    def is_en_passant_move(self, moving_piece, row2, col2):
        if moving_piece.lower() != "p":
            return False

        if self.en_passant_target is None:
            return False

        if (row2, col2) != self.en_passant_target:
            return False

        if self.board[row2][col2] != "-":
            return False

        return True
    
    def get_en_passant_moves(self, player, row, col):
        en_passant_moves = []

        if self.en_passant_target is None:
            return en_passant_moves

        if self.en_passant_victim_player == player:
            return en_passant_moves

        target_row, target_col = self.en_passant_target
        capture_row, capture_col = self.en_passant_capture_square

        direction = -1 if player == "white" else 1

        # pawn must move diagonally into the en passant target square
        if target_row == row + direction and abs(target_col - col) == 1:
            # captured pawn must be beside this pawn
            if capture_row == row and abs(capture_col - col) == 1:
                en_passant_moves.append((target_row, target_col))

        return en_passant_moves

    
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
        
        moving_piece = self.board[row1][col1]

        en_passant_move = self.is_en_passant_move(moving_piece, row2, col2)

        if en_passant_move:
            capture_row, capture_col = self.en_passant_capture_square
            captured_piece = self.board[capture_row][capture_col]
        else:
            captured_piece = self.board[row2][col2]

        if captured_piece != "-":
            points = piece_values[captured_piece.lower()]
            
            currP = self.get_current_player()

            currP.update_score(points)
            currP.capture_piece(get_piece_name(captured_piece))

        # remove captured en passant pawn
        if en_passant_move:
            capture_row, capture_col = self.en_passant_capture_square
            self.board[capture_row][capture_col] = "-"

        # move main piece
        self.board[row2][col2] = self.board[row1][col1]
        self.board[row1][col1] = "-"

        if self.should_promote_pawn(moving_piece, row2):
            self.promote_pawn(row2, col2)

        # if castling, move rook too
        self.move_rook_for_castling(row1, col1, row2, col2)

        # update castling/en passant state
        self.update_special_move_state(moving_piece, row1, col1, row2, col2)

        print(f"{self.current_p} moves from {from_pos} to {to_pos}")
        self.switch_turn()

    def get_moves_for_player(self, player):
        moves = []

        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]

                # skip empty squares
                if piece == "-":
                    continue
                    
                # skip opponent pieces
                if not validate_player_move(player, piece):
                    continue

                # create the piece object
                piece_obj = create_piece_object(piece, player)

                if not piece_obj:
                    continue
                    
                # get legal moves for that piece
                opp_legal_moves = self.get_legal_moves(player, r, c, piece_obj)

                for row2, col2 in opp_legal_moves:
                    moves.append((r, c, row2, col2))

        return moves

    def get_bot_moves(self):
        return self.get_moves_for_player(self.current_p)


    def score_easy_move(self, r2, c2):
        score = 0

        target_piece = self.board[r2][c2].lower()

        if target_piece != "-":
            score += piece_values[target_piece]

        return score
    
    def easyBot_move(self):
        easy_moves = self.get_bot_moves()

        if not easy_moves:
            return None
        
        pawn_moves = []
        non_pawn_moves = []
        
        scored_moves = []
        curr_score = 0
        # best_moves = []

        for move in easy_moves:
            r1, c1, r2, c2 = move
            curr_score = self.score_easy_move(r2, c2)

            scored_move = (curr_score, r1, c1, r2, c2)
            scored_moves.append(scored_move)

            moving_piece = self.board[r1][c1].lower()

            if moving_piece == "p":
                pawn_moves.append(scored_move)
            else:
                non_pawn_moves.append(scored_move)

            

        if non_pawn_moves and random.random() < 0.35:
            move_pool = non_pawn_moves
        else:
            scored_moves.sort(key=lambda move: move[0], reverse=True)
            move_pool = scored_moves[:8]

        final = random.choice(move_pool)

        score, row1, col1, row2, col2 = final

        from_square = convert_to_chess_notation(row1, col1)
        to_square = convert_to_chess_notation(row2, col2)

        return from_square, to_square

    # temp, find one already in program: 
    def get_enemy_player(self, player):
        if player == "white":
            return "black" 
        return "white"
    

    def score_med_move(self, r1, c1, r2, c2):
        score = 0

        center_squares = {(3, 3), (3, 4), (4, 3), (4, 4)}

        moving_piece = self.board[r1][c1].lower()
        target_piece = self.board[r2][c2].lower()

        moving_score = piece_values[moving_piece]

        if target_piece != "-":
            target_score = piece_values[target_piece]

            score += target_score * 10
            score -= moving_score

        # reward en passant
        if self.is_en_passant_move(self.board[r1][c1], r2, c2):
            score += piece_values["p"] * 10
            score -= moving_score

        # Rule: reward center control
        if (r2, c2) in center_squares:
            score += 2

        # reward pawn promotion
        if moving_piece == "p":
            if self.current_p == "white" and r2 == 0:
                score += 90
            elif self.current_p == "black" and r2 == 7:
                score += 90

        # reward castling
        if moving_piece == "k" and r1 == r2 and abs(c2 - c1) == 2:
            score += 8

        # reward developing knights and bishops
        if moving_piece in ["n", "b"]:
            if self.current_p == "white" and r1 == 7:
                score += 3
            elif self.current_p == "black" and r1 == 0:
                score += 3

        # simulate move
        move_info = self.simulate_move(r1, c1, r2, c2)
        enemy = self.get_enemy_player(self.current_p)

        # punish move that creates danger
        if self.is_square_attacked(r2, c2, enemy):
            score -= moving_score * 3

        # reward check/checkmate
        if self.is_checkmate(enemy):
            score += 1000

        elif self.is_in_check(enemy):
            score += 5

        self.undo_move(r1, c1, r2, c2, move_info)

        return score
    
    

    def medBot_move(self):
        med_moves = self.get_bot_moves()

        if not med_moves:
            return None
        
        scored_moves = []
        curr_score = 0
        best_moves = []

        for move in med_moves:
            r1, c1, r2, c2 = move
            curr_score = self.score_med_move(r1, c1, r2, c2)
            scored_moves.append((curr_score, r1, c1, r2, c2))

        highest = max(scored_moves, key=lambda move: move[0])

        for move in scored_moves:
            if move[0] == highest[0]:
                best_moves.append(move) 

        final = random.choice(best_moves)

        score, row1, col1, row2, col2 = final

        from_square = convert_to_chess_notation(row1, col1)
        to_square = convert_to_chess_notation(row2, col2)

        return from_square, to_square
    
    def simulate_search_move(self, r1, c1, r2, c2):
        moving_piece = self.board[r1][c1]

        move_info = self.simulate_move(r1, c1, r2, c2)

        promoted = False

        if moving_piece == "P" and r2 == 0:
            self.board[r2][c2] = "Q"
            promoted = True

        elif moving_piece == "p" and r2 == 7:
            self.board[r2][c2] = "q"
            promoted = True

        return move_info, promoted, moving_piece


    def undo_search_move(self, r1, c1, r2, c2, search_info):
        move_info, promoted, original_piece = search_info

        if promoted:
            self.board[r2][c2] = original_piece

        self.undo_move(r1, c1, r2, c2, move_info)
    
    def evaluate_board(self, bot_player):
        score = 0
        center_squares = {(3, 3), (3, 4), (4, 3), (4, 4)}
        white_castled_squares = {(7, 6),  (7, 2)}
        black_castled_squares = {(0, 6),  (0, 2)}


        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]

                if piece == "-":
                    continue

                piece_type = piece.lower()
                value = piece_values[piece_type]

                if bot_player == "white":
                    is_bot_piece = piece.isupper()
                else:
                    is_bot_piece = piece.islower()

                # Rule 1: material score
                if is_bot_piece:
                    score += value
                else:
                    score -= value

                # Rule 2: reward center control
                if (r, c) in center_squares:
                    if is_bot_piece:
                        score += 1
                    else:
                        score -= 1

                # Rule 3: reward developed knights and bishops
                if piece_type in ["n", "b"]:
                    developed = False

                    # white knight/bishop developed if it left row 7
                    if piece.isupper() and r != 7:
                        developed = True

                    # black knight/bishop developed if it left row 0
                    elif piece.islower() and r != 0:
                        developed = True

                    if developed:
                        if is_bot_piece:
                            score += 1
                        else:
                            score -= 1

                # Rule 4: reward castled king position
                if piece_type == "k":
                    castled = False

                    if piece.isupper() and (r, c) in white_castled_squares:
                        castled = True

                    elif piece.islower() and (r, c) in black_castled_squares:
                        castled = True

                    if castled:
                        if is_bot_piece:
                            score += 2
                        else:
                            score -= 2

                # Rule 5: pawn structure
                if piece_type == "p":
                    if self.is_passed_pawn(r, c, piece):
                        if is_bot_piece:
                            score += 2
                        else:
                            score -= 2

                    if self.is_doubled_pawn(c, piece):
                        if is_bot_piece:
                            score -= 1
                        else:
                            score += 1

        # Rule 6: mobility bonus
        enemy = self.get_enemy_player(bot_player)

        if self.is_in_check(enemy):
            score += 3

        if self.is_in_check(bot_player):
            score -= 3

        # mobility bonus
        bot_moves = len(self.get_moves_for_player(bot_player))
        enemy_moves = len(self.get_moves_for_player(enemy))

        mobility_difference = bot_moves - enemy_moves

        score += mobility_difference * 0.1


        return score
    
    def order_moves(self, player, moves):
        ordered_candidates = []

        for m in moves:
            ordering_score = 0
            r1, c1, r2, c2 = m
            mov = self.board[r1][c1].lower()
            targ = self.board[r2][c2].lower()


            if targ != "-":
                targ_val = piece_values[targ]

                ordering_score += targ_val * 10
            
            # reward pawn promotion
            if mov == "p":
                if player == "white" and r2 == 0:
                    ordering_score += 90
                elif player == "black" and r2 == 7:
                    ordering_score += 90

            # reward castling
            if mov == "k" and r1 == r2 and abs(c2 - c1) == 2:
                ordering_score += 8

            # reward developing knights and bishops
            if mov in ["n", "b"]:
                if player == "white" and r1 == 7:
                    ordering_score += 3
                elif player == "black" and r1 == 0:
                    ordering_score += 3

            ordered_candidates.append((ordering_score, m))
        
        highest_first = sorted(ordered_candidates, key=lambda item: item[0], reverse=True)

        ordered_moves = [item[1] for item in highest_first]

        return ordered_moves
    

    def get_board_key(self):
        return tuple(tuple(row) for row in self.board)
    
    def get_cache_key(self, depth, player_to_move, bot):
        castling_state = (
            self.king_moved["white"],
            self.king_moved["black"],
            self.rook_moved["white"]["kingside"],
            self.rook_moved["white"]["queenside"],
            self.rook_moved["black"]["kingside"],
            self.rook_moved["black"]["queenside"]
        )

        return (self.get_board_key(), depth, player_to_move, bot, self.en_passant_target, castling_state)

    def count_pieces(self):
        count = 0
        for r in range(8):
            for c in range(8):
                curr_piece = self.board[r][c]

                if curr_piece != "-":
                    count += 1

        return count
    
    def is_doubled_pawn(self, col, pawn):
        count = 0

        for r in range(8):
            if self.board[r][col] == pawn:
                count += 1

        return count > 1


    def is_passed_pawn(self, row, col, pawn):
        if pawn == "P":
            enemy_pawn = "p"
            rows_to_check = range(row - 1, -1, -1)

        elif pawn == "p":
            enemy_pawn = "P"
            rows_to_check = range(row + 1, 8)

        else:
            return False

        for r in rows_to_check:
            for dc in [-1, 0, 1]:
                check_col = col + dc

                if 0 <= check_col < 8:
                    if self.board[r][check_col] == enemy_pawn:
                        return False

        return True
        
    def minimax(self, depth, player_to_move, bot, alpha, beta, search_cache):
        if depth == 0:
            return self.evaluate_board(bot)
        
        cache_key = self.get_cache_key(depth, player_to_move, bot)

        if cache_key in search_cache:
            return search_cache[cache_key]
        
        moves = self.get_moves_for_player(player_to_move)
        moves = self.order_moves(player_to_move, moves)

        if len(moves) == 0:
            if self.is_in_check(player_to_move):
                if player_to_move == bot:
                    return -99999 - depth
                else:
                    return 99999 + depth
                
            else:
                return 0
 
        

        enemy = self.get_enemy_player(player_to_move)
        
        if player_to_move == bot:

            best_score = -99999
            pruned = False

            for m in moves:
                r1, c1, r2, c2 = m

                sim_move = self.simulate_search_move(r1, c1, r2, c2)


                score = self.minimax(depth - 1, enemy, bot, alpha, beta, search_cache)

                self.undo_search_move(r1, c1, r2, c2, sim_move)

                if score > best_score:
                    best_score = score

                alpha = max(alpha, best_score)

                if beta <= alpha:
                    pruned = True
                    break
            
            if not pruned:
                search_cache[cache_key] = best_score  

            return best_score
        
        else:
            best_score = 99999
            pruned = False

            for m in moves:
                r1, c1, r2, c2 = m
                sim_move = self.simulate_search_move(r1, c1, r2, c2)


                score = self.minimax(depth - 1, enemy, bot, alpha, beta, search_cache)

                self.undo_search_move(r1, c1, r2, c2, sim_move)

                if score < best_score:
                    best_score = score

                beta = min(beta, best_score)

                if beta <= alpha:
                    pruned = True
                    break

            if not pruned:
                search_cache[cache_key] = best_score
                
            return best_score


    def hardBot_move(self):

        search_cache = {}
        piece_count = self.count_pieces()

        if piece_count > 24:
            depth = 2
        elif piece_count > 12:
            depth = 3
        else:
            depth = 4


        alpha = -99999
        beta = 99999


        bot = self.current_p
        enemy = self.get_enemy_player(bot)

        moves = self.get_moves_for_player(bot)
        moves = self.order_moves(bot, moves)


        if len(moves) == 0:
            return None
        
        best_score = -99999
        best_moves = []

        for m in moves:
            r1, c1, r2, c2 = m

            sim_move = self.simulate_search_move(r1, c1, r2, c2)

            score = self.minimax(depth - 1, enemy, bot, alpha, beta, search_cache)

            self.undo_search_move(r1, c1, r2, c2, sim_move)

            if score > best_score:
                best_score = score
                best_moves = [m]

            elif score == best_score:
                best_moves.append(m)

        final = random.choice(best_moves)

        row1, col1, row2, col2 = final

        from_square = convert_to_chess_notation(row1, col1)
        to_square = convert_to_chess_notation(row2, col2)

        return from_square, to_square


###############  game code: ####################################################

def get_game_mode():
    prompt = "Select mode: user or bot? (user/bot): "
    while True:
        mode = input(prompt).strip().lower()
        if mode in ("user", "u"):
            return "user"
        if mode in ("bot", "b"):
            return "bot"
        print("Please enter 'user' or 'bot'.")


def get_bot_difficulty():
    prompt = "Select bot difficulty (easy/medium/hard): "
    while True:
        difficulty = input(prompt).strip().lower()
        if difficulty in ("easy", "medium", "hard"):
            return difficulty
        print("Please enter 'easy', 'medium', or 'hard'.")

def get_bot_color():
    prompt = "select the color the bot should play as(black/white): "
    while True:
        color = input(prompt).strip().lower()
        if color in ("black", "white"):
            return color
        print("please select either black or white.")


def print_turn_header(game):
    current_color = game.current_p
    if game.is_in_check(current_color):
        print("CHECK! You are in check.")
        
    print_board(game.board)
    current_player = game.get_current_player()
    print(f"player at turn: {current_player.get_player_info()}")
    print(f"captured pieces: {current_player.get_captured_list()}")


def show_end_game(game, player_color):
    if game.is_checkmate(player_color):
        print_board(game.board)
        winner_color = "black" if player_color == "white" else "white"
        print(f"CHECKMATE! {player_color.capitalize()} loses.")
        return {"outcome": "checkmate", "winner": winner_color}

    if game.is_stalemate(player_color):
        print_board(game.board)
        print("STALEMATE! Draw.")
        return {"outcome": "draw"}

    return None


def perform_human_turn(game):
    from_piece = input("what piece do you want to move?: ")
    from_piece = game.validate_from(from_piece)
    to_piece = input("where should the piece go?: ")
    to_piece = game.validate_to(to_piece)

    game.make_move(from_piece, to_piece)


def perform_bot_turn(game, difficulty):
    # obtain bot move(s) according to difficulty
    if difficulty == "easy":
        bot_from_move, bot_to_move = game.easyBot_move()

    if difficulty == "medium":
        bot_from_move, bot_to_move  = game.medBot_move()

    if difficulty == "hard":
        bot_from_move, bot_to_move = game.hardBot_move()


    # if bot_from_move returned a (from,to) tuple, unpack it
    if isinstance(bot_from_move, tuple):
        from_piece, to_piece = bot_from_move
    else:
        from_piece = bot_from_move
        to_piece = bot_to_move

    # validate we have both squares
    if not from_piece or not to_piece:
        print("Bot has no legal moves.")
        return None

    print(f"Bot chooses {from_piece} to {to_piece}")

    game.make_move(from_piece, to_piece)


def log_in_prompt():
    u_name = input("welcome back! please enter your username: ")
    p_word = input("please enter your password: ")

    return u_name, p_word

def sign_up_prompt():
    u_name = input("welcome to the chess app. Please enter your name/username: ")
    p_word1 = input("please set a password: ")
    p_word2 = input("please confirm password: ")

    while p_word1 != p_word2:
        print("passwords did not match")
        p_word1 = input("please set a password: ")
        p_word2 = input("please confirm password: ")

    return u_name, p_word1

create_tables()

# log in/ sign up
print("Welcome to chess!\n")
choice = input("\nlog - log in \n sign - sign up \n guest - continue as guest\n your choice: ").strip().lower()
player_name = ""
player_elo = 0
user_info = None

finished = False
while not finished:
    if choice == "log":
        # if db log in matches:
        # continue to game
        # set user name

        # if not:
        # prompt inputs again
        # suggest sign up
        user, passw = log_in_prompt()
        entered_password_hash = hash_password(passw)

        user_info = get_player(user)


        while user_info is None:
            print("\nuser not found in database")
            
            s = input("\ncontinue to sign up instead? (Y/N): ")
            if s.strip().upper() == "Y":
                choice = "sign"
                break

            print("\nPlease try again:\n")
            user, passw = log_in_prompt()
            entered_password_hash = hash_password(passw)


        if choice == "sign":
            continue

        stored_hashed_passw = user_info[2]

        # user found in DB, check password
        while entered_password_hash != stored_hashed_passw:
            passw = input("password incorrect, please try again: ")
            entered_password_hash = hash_password(passw)

        print("log in successful, welcome back.")
        player_name = user_info[1]
        player_elo = user_info[3]
        break
        


    if choice == "sign":
        
        # if db account create succesful:
        # continue to game
        # create db entry and set user name

        # if account already exists:
        # prompt sign up again
        # suggest login

        user, passw = sign_up_prompt()
        hashed_password = hash_password(passw)

        new_id = create_player(user, hashed_password)

        while new_id is None:
            print("\nplayer already exists, please try again")
            l = input("continue to log in instead? (Y/N): ")
            if l.strip().upper() == "Y":
                choice = "log"
                break

            user, passw = sign_up_prompt()
            hashed_password = hash_password(passw)
            new_id = create_player(user, hashed_password)

        if choice == "log":
            continue

        print("sign up successful, welcome.")
        player_name = user
        break


    if choice == "guest":
        # go straight into being prompted to play against player or bot
        player_name = "guest"
        print("welcome to the chess app, enjoy and good luck.")
        break

    if choice not in {"log", "sign", "guest"}:
        print("Invalid option. Please choose log, sign, or guest.")
        choice = input("\nlog - log in \n sign - sign up \n guest - continue as guest\n").strip().lower()
        continue


print(f"welcome {player_name}")

mode = get_game_mode()
bot_difficulty = None
bot_color = None
load_turn = None
loaded_game = None

# chosen to play against bot, can have saved game
human_player = None
human_player_id = None

if mode == "bot":
    # prompt to load game or start a new game
    new_load = "new"

    # guests will not have saved games, skip choice to load game
    if player_name != "guest":
        new_load = input("Play new game(new) or load existing(load)?: ").strip().lower()

        while new_load not in {"new", "load"}:
            print("Invalid option. Please choose a valid option.")
            new_load = input("Play new game(new) or load existing(load)?: ").strip().lower()

    if new_load == "load" and player_name != "guest":
        saved_games = get_all_saved_games(user_info[0])

        if saved_games:
            print("Saved bot games:")
            for index, save in enumerate(saved_games, start=1):
                loaded = load_saved_game(save[0])
                print(f"{index}. {save[3]} | turn: {loaded['current_turn']} | difficulty: {loaded['bot_difficulty']}")

            num_games = len(saved_games)
            while True:
                try:
                    game_choice = int(input(f"What game do you want to load? (1 - {num_games}): ").strip())
                    if 1 <= game_choice <= num_games:
                        break
                except ValueError:
                    game_choice = None

                print("Please enter a valid number.")

            save_id = saved_games[game_choice - 1][0]
            loaded_game = load_saved_game(save_id)
            chess_board = loaded_game["board"]
            load_turn = loaded_game["current_turn"]
            bot_difficulty = loaded_game["bot_difficulty"]
            bot_color = loaded_game.get("bot_color")

        else:
            print("No saved games found, starting new game.")
            new_load = "new"

    if new_load == "new" or player_name == "guest":
        bot_difficulty = get_bot_difficulty()
        bot_color = get_bot_color()
        print(f"Bot difficulty set to {bot_difficulty} and will be playing as {bot_color}.")

        if bot_color == "black":
            player1 = Player(f"{player_name} / white", get_starting_elo(player_elo))
            player2 = Player("Bot / black")

        elif bot_color == "white":
            player1 = Player("Bot / white")
            player2 = Player(f"{player_name} / black", get_starting_elo(player_elo))

    else:
        if bot_color == "black":
            player1 = Player(f"{player_name} / white", get_starting_elo(player_elo))
            player2 = Player("Bot / black")
        else:
            player1 = Player("Bot / white")
            player2 = Player(f"{player_name} / black", get_starting_elo(player_elo))


# player chooses to play against another player, no saved game logic needed
else:
    player1 = Player(f"{player_name} white", get_starting_elo(player_elo))
    player2 = Player("Player 2 / black")



chess_game = Game(chess_board, player1, player2)
if load_turn is not None:
    chess_game.current_p = load_turn

if player_name != "guest" and user_info is not None:
    human_player = next((player for player in chess_game.players.values() if player_name in player.name), None)
    human_player_id = user_info[0]


while True:
    current_color = chess_game.current_p

    # check for immediate game-over conditions before the next turn
    end_state = show_end_game(chess_game, current_color)
    if end_state is not None:
        apply_game_result_elo(chess_game, end_state, human_player, human_player_id)
        break

    print_turn_header(chess_game)

    # select human or bot move based on current mode and player
    if mode == "bot" and current_color == bot_color:
        perform_bot_turn(chess_game, bot_difficulty)
    else:
        perform_human_turn(chess_game)

    next_color = chess_game.current_p

    # check for game-over conditions after the move
    end_state = show_end_game(chess_game, next_color)
    if end_state is not None:
        apply_game_result_elo(chess_game, end_state, human_player, human_player_id)
        break

    cont = input("continue?(Y/N): ").strip().upper()
    while cont not in {"Y", "N"}:
        print("Invalid option. Please choose a valid option.")
        cont = input("save game?(Y/N): ").strip().upper()

    if cont == "N":
        if mode == "bot":
            # guest cant save game, just exit game
            if player_name == "guest":
                print("goodbye!")
                break

            # prompt to save game
            q_save = input("save game?(Y/N): ").strip().upper()
            while q_save not in {"Y", "N"}:
                print("Invalid option. Please choose a valid option.")
                q_save = input("save game?(Y/N): ").strip().upper()

            # stores current board and required info
            if q_save == "Y":
                save_id = save_game(
                    player_id=user_info[0],
                    board=chess_game.board,
                    current_turn=chess_game.current_p,
                    bot_difficulty=bot_difficulty,
                    bot_color=bot_color,
                    time_limit_seconds=0,
                    player_time_left=0,
                )
                print(f"Game saved. Save ID: {save_id}, goodbye!")
                break
            else:
                print("exiting without saving, goodbye!")
                break
        
        elif mode == "player":
            draw_offer = input("Offer a draw? (Y/N): ").strip().upper()
            while draw_offer not in {"Y", "N"}:
                print("Invalid option. Please choose a valid option.")
                draw_offer = input("Offer a draw? (Y/N): ").strip().upper()

            if draw_offer == "Y":
                print("Draw accepted. No rating changes were made.")
                break

            resign = input("Resign and end the game? (Y/N): ").strip().upper()
            while resign not in {"Y", "N"}:
                print("Invalid option. Please choose a valid option.")
                resign = input("Resign and end the game? (Y/N): ").strip().upper()

            if resign == "Y":
                if human_player is not None and human_player_id is not None:
                    losing_color = chess_game.current_p
                    winning_color = "black" if losing_color == "white" else "white"
                    result = {"outcome": "resign", "winner": winning_color}
                    apply_game_result_elo(chess_game, result, human_player, human_player_id)
                print("You resigned. Game over.")
                break

            print("Continuing the game.")
