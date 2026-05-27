from move_validator import *
from pieces import *
from utils import *
from board import *


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

        if self.is_en_passant_move(moving_piece, row1, col1, row2, col2):
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
    
    def get_valid_coordinate(self, prompt):
        pos = input(prompt)

        while not is_valid(pos):
            print("invalid coordinate\n")
            pos = input(prompt)

        return pos
    
    def validate_from(self, from_pos):
        # ensure move is valid

        while not is_valid(from_pos):
            print("invalid coordinate\n")
            from_pos = self.get_valid_coordinate("please select a valid piece to move: ")
                

        # get piece
        row1, col1, selected_piece = self.get_piece_at_position(from_pos)

        # make sure player selection is not an empty square
        while True:
            
            row1, col1, selected_piece = self.get_piece_at_position(from_pos)

            if selected_piece != "-":
                break

            print("no piece at selected square\n")
            from_pos = self.get_valid_coordinate("please select a different piece to move: ")


        # make sure that player owns the piece they want to move
        while not validate_player_move(self.current_p, selected_piece):

            print("that piece does not belong to you\n")
            from_pos = self.get_valid_coordinate("please select a different piece to move: ")

            row1, col1, selected_piece = self.get_piece_at_position(from_pos)

            while selected_piece == "-":
                print("no piece at selected square\n")
                from_pos = self.get_valid_coordinate("please select a different piece to move: ")

                row1, col1, selected_piece = self.get_piece_at_position(from_pos)
            

        # get all legal moves for selected piece on board
        piece_object = create_piece_object(selected_piece, self.current_p)
        self.legal_moves = self.get_legal_moves(self.current_p, row1, col1, piece_object)


        # if piece has no legal moves, prompt again
        while len(self.legal_moves) == 0:

            print("that piece has no legal moves\n")
            from_pos = self.get_valid_coordinate("please select a different piece to move: ")

            row1, col1, selected_piece = self.get_piece_at_position(from_pos)

                # prevent empty square
            while selected_piece == "-":
                print("no piece at selected square\n")
                from_pos = self.get_valid_coordinate("please select a different piece to move: ")

                row1, col1, selected_piece = self.get_piece_at_position(from_pos)

            # prevent selecting enemy piece
            while not validate_player_move(self.current_p, selected_piece):

                print("that piece does not belong to you\n")
                from_pos = self.get_valid_coordinate("please select a different piece to move: ")

                row1, col1, selected_piece = self.get_piece_at_position(from_pos)

            # self.legal_moves = list_moves(selected_piece, row1, col1, self.current_p, self.board)
            piece_object = create_piece_object(selected_piece, self.current_p)
            self.legal_moves = self.get_legal_moves(self.current_p, row1, col1, piece_object)


        print_possible_moves(self.legal_moves, self.board)
        # show all legal moves on board

        # print board
        print_board(self.board, self.legal_moves)

        return from_pos


    def validate_to(self, to_pos):

        while True:

            while not is_valid(to_pos):
                print("invalid destination\n")
                to_pos = input("please select a different place to move to: ")

            row2, col2 = convert_move(to_pos)

            if (row2, col2) in self.legal_moves:
                return to_pos

            print("illegal move for that piece\n")
            to_pos = input("please select a different place to move to: ")

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
    
    def is_en_passant_move(self, moving_piece, row1, col1, row2, col2):
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

        en_passant_move = self.is_en_passant_move(moving_piece, row1, col1, row2, col2)

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