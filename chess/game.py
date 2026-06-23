from move_validator import *
from pieces import *
from utils import *
from board import *
import random


###############  game controller exercise ########################################

class Game:
    def __init__(self, u_board, pWhite, pBlack):
        self.board = u_board
        self.current_p = "white"
        self.turn_count = 0
        self.legal_moves = []
        self.last_captured_piece = None

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
    

    def should_promote_pawn(self, piece, row):

        if piece.lower() != "p":
            return False

        if self.current_p == "white" and row == 0:
            return True

        if self.current_p == "black" and row == 7:
            return True

        return False
    
    def promote_pawn(self, row, col, promotion_choice="q"):

        promotion_options = {
            "q": "queen",
            "r": "rook",
            "b": "bishop",
            "n": "knight"
        }

        choice = promotion_choice.lower()

        # Default to queen if something invalid is passed
        if choice not in promotion_options:
            choice = "q"

        if self.current_p == "white":
            self.board[row][col] = choice.upper()
        else:
            self.board[row][col] = choice

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

    
    def make_move(self, row1, col1, row2, col2, promotion_choice="q"):

        self.last_captured_piece = None
        
        moving_piece = self.board[row1][col1]

        en_passant_move = self.is_en_passant_move(moving_piece, row2, col2)

        if en_passant_move:
            capture_row, capture_col = self.en_passant_capture_square
            captured_piece = self.board[capture_row][capture_col]
        else:
            captured_piece = self.board[row2][col2]

        if captured_piece != "-":
            self.last_captured_piece = captured_piece
            
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
            self.promote_pawn(row2, col2, promotion_choice)

        # if castling, move rook too
        self.move_rook_for_castling(row1, col1, row2, col2)

        # update castling/en passant state
        self.update_special_move_state(moving_piece, row1, col1, row2, col2)

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
