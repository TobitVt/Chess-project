
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
            # one square forward
            if row - 1 >= 0 and board[row - 1][col] == "-":
                self.valid_moves.append((row - 1, col))

                # first move two squares
                if row == 6 and board[row - 1][col] == "-" and board[row - 2][col] == "-":
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
                if row == 1 and board[row + 1][col] == "-" and board[row + 2][col] == "-":
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

        enemy = "black" if self.player == "white" else "white"

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
                    break

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

    piece_class = piece_classes[piece_symbol.lower()]
    if not piece_class:
        return None
    return piece_class(piece_symbol, player)