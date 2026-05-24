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

                if validate_player_move(enemy_player, piece):
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
        king_row, king_col = self.find_king(player)

        enemy = "black" if player == "white" else "white"
        
        if self.is_square_attacked(king_row, king_col, enemy):
            return True
        else:
            return False
        
    def simulate_move(self, row1, col1, row2, col2):
        captured_piece = self.board[row2][col2]

        self.board[row2][col2] = self.board[row1][col1]
        self.board[row1][col1] = "-"

        return captured_piece
    
    def undo_move(self, row1, col1, row2, col2, captured_piece):
        self.board[row1][col1] = self.board[row2][col2]
        self.board[row2][col2] = captured_piece


    def is_legal_after_move(self, row1, col1, row2, col2):
        captured_piece = self.simulate_move(row1, col1, row2, col2)

        player = self.current_p
        in_check = self.is_in_check(player)

        self.undo_move(row1, col1, row2, col2, captured_piece)

        return not in_check

    def get_legal_moves(self, row1, col1, piece_object):

        pseudo_moves = piece_object.get_moves(row1, col1, self.board)

        legal_moves = []

        for row2, col2 in pseudo_moves:
            if self.is_legal_after_move(row1, col1, row2, col2):
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
                legal_moves = self.get_legal_moves(r, c, piece_obj)

                if len(legal_moves) > 0:
                    return True

        return False
    
    def is_checkmate(self, player):
        return self.is_in_check(player) and not self.has_any_legal_moves(player)
    
    def is_stalemate(self, player):
        return not self.is_in_check(player) and not self.has_any_legal_moves(player)
        
    
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

            while selected_piece == "-":
                print("no piece at selected square\n")
                from_pos = input("please select a different piece to move: ")

                row1, col1 = convert_move(from_pos)
                selected_piece = self.board[row1][col1]
            

        # get all legal moves for selected piece on board
        piece_object = create_piece_object(selected_piece, self.current_p)
        self.legal_moves = self.get_legal_moves(row1, col1, piece_object)


        # if piece has no legal moves, prompt again
        while len(self.legal_moves) == 0:

            print("that piece has no legal moves\n")
            from_pos = input("please select a different piece to move: ")

            row1, col1 = convert_move(from_pos)
            selected_piece = self.board[row1][col1]

                # prevent empty square
            while selected_piece == "-":
                print("no piece at selected square\n")
                from_pos = input("please select a different piece to move: ")

                row1, col1 = convert_move(from_pos)
                selected_piece = self.board[row1][col1]

            # prevent selecting enemy piece
            while not validate_player_move(self.current_p, selected_piece):

                print("that piece does not belong to you\n")
                from_pos = input("please select a different piece to move: ")

                row1, col1 = convert_move(from_pos)
                selected_piece = self.board[row1][col1]

            # self.legal_moves = list_moves(selected_piece, row1, col1, self.current_p, self.board)
            piece_object = create_piece_object(selected_piece, self.current_p)
            self.legal_moves = self.get_legal_moves(row1, col1, piece_object)


        print_possible_moves(self.legal_moves, self.board)
        # show all legal moves on board
        highlight_moves(self.board, self.legal_moves)


        # print board
        print_board(self.board)

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
        

        captured_piece = self.board[row2][col2]

        if captured_piece != "-" and captured_piece != "#":
            points = piece_values[captured_piece.lower()]
            
            currP = self.get_current_player()

            currP.update_score(points)
            currP.capture_piece(get_piece_name(captured_piece))
            
            

        self.board[row2][col2] = self.board[row1][col1] 
        self.board[row1][col1] = "-"

        print(f"{self.current_p} moves from {from_pos} to {to_pos}")
        self.switch_turn()
        clear_highlights(self.board)


 