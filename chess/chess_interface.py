from PySide6.QtWidgets import (
    QInputDialog,
    QGridLayout,
    QMainWindow,
    QPushButton,
    QWidget
)

from pathlib import Path

from PySide6.QtCore import QSize, QTimer
from PySide6.QtGui import QIcon

from pieces import create_piece_object

from move_validator import *
from utils import *

# stores path to piece images in global variable
ASSETS_PATH = Path(__file__).resolve().parent.parent / "assets" / "pieces"

# create list of pieces in order
pieces = ["r", "n", "b", "q", "k", "b", "n", "r"]

# dictionary for mapping piece images to pieces on board
piece_images = {
    "K": "white_king.svg",
    "Q": "white_queen.svg",
    "R": "white_rook.svg",
    "B": "white_bishop.svg",
    "N": "white_knight.svg",
    "P": "white_pawn.svg",

    "k": "black_king.svg",
    "q": "black_queen.svg",
    "r": "black_rook.svg",
    "b": "black_bishop.svg",
    "n": "black_knight.svg",
    "p": "black_pawn.svg"
}


class ChessBoard(QMainWindow):
    def __init__(self, game):
        super().__init__()

        self.game = game
        self.buttons = []
        self.selected = None
        self.selected_moves = []

        self.game_over = False

        # ask user for bot color
        chosen_colour, accepted = QInputDialog.getItem(
            self,
            "Choose colour",
            "Play as:",
            ["White", "Black"],
            0,
            False
        )

        if accepted:
            self.human_player = chosen_colour.lower()
        else:
            self.human_player = "white"

        self.bot_player = (
            "black" if self.human_player == "white" else "white"
        )
        
        # ask user for bot difficulty
        difficulty, accepted = QInputDialog.getItem(
            self,
            "Choose difficulty",
            "Select bot difficulty:",
            ["Easy", "Medium", "Hard"],
            0,
            False
        )

        if accepted:
            self.bot_difficulty = difficulty.lower()
        else:
            self.bot_difficulty = "easy"

        # create main window

        self.setWindowTitle("Chess board")
        self.resize(900, 900)

        main_container = QWidget()
        grid_layout = QGridLayout()

        grid_layout.setSpacing(0)
        grid_layout.setContentsMargins(20, 20, 20, 20)


        for row in range(8):
            button_row = []

            for col in range(8):
                # create buttons
                block = QPushButton()
                block.setMinimumSize(100, 110)
                block.setIconSize(QSize(75, 75))

                block.clicked.connect(
                    lambda checked=False, r=row, c=col:
                    self.handle_square_click(r, c)
                )

                # add widgets to grid and buttons to list
                grid_layout.addWidget(block, row, col)
                button_row.append(block)

            self.buttons.append(button_row)

        main_container.setLayout(grid_layout)
        self.setCentralWidget(main_container)

        self.refresh_board()
        self.update_game_status()

        # The white bot must make the opening move
        if self.bot_player == "white":
            QTimer.singleShot(500, self.run_bot_turn)
    

    def refresh_board(self):

        self.setWindowTitle(f"Chess - {self.bot_difficulty.capitalize()} bot")

        checked_king = None

        if self.game.is_in_check(self.game.current_p):
            checked_king = self.game.find_king(self.game.current_p)

        for row  in range(8):
            for col  in range(8):
                button = self.buttons[row][col]
                piece = self.game.board[row][col]

                # Remove the previous icon
                button.setIcon(QIcon())

                if piece != "-":
                    image_path = ASSETS_PATH / piece_images[piece]
                    button.setIcon(QIcon(str(image_path)))

                # King currently in check
                if checked_king == (row, col):
                    colour = "#E53935"

                # Highlight the selected square
                elif self.selected == (row, col):
                    colour = "#FDD835"

                # Valid destination
                elif (row, col) in self.selected_moves:
                    colour = "#66BB6A"

                # gives alternating blocks different colours for checkered look
                elif (row + col) % 2 == 0:
                    colour = "#D7CCC8"
                else:
                    colour = "#5D4037"

                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {colour};
                        border: none;
                    }}
                """)

    def update_game_status(self):
        player = self.game.current_p
        player_name = player.capitalize()

        in_check = self.game.is_in_check(player)
        has_legal_moves = self.game.has_any_legal_moves(player)

        if in_check and not has_legal_moves:
            winner = "Black" if player == "white" else "White"

            self.statusBar().showMessage(
                f"Checkmate! {winner} wins."
            )

            self.game_over = True

        elif not in_check and not has_legal_moves:
            self.statusBar().showMessage(
                "Stalemate! The game is a draw."
            )

            self.game_over = True

        elif in_check:
            self.statusBar().showMessage(
                f"{player_name} is in check!"
            )

        else:
            self.statusBar().showMessage(
                f"{player_name}'s turn"
            )

    def run_bot_turn(self):
        if self.game_over:
            return

        perform_bot_turn(self.game, self.bot_difficulty)

        self.refresh_board()
        self.update_game_status()

    def handle_square_click(self, row, col):
        if self.game_over:
            return  
        
        if self.game.current_p == self.bot_player:
            return
        
        piece = self.game.board[row][col]


        # Move the selected piece
        if self.selected is not None and (row, col) in self.selected_moves:
            start_row, start_col = self.selected

            # Get the piece from the origin square
            moving_piece = self.game.board[start_row][start_col]

            promotion_choice = None

            # Ask what the pawn should become
            if moving_piece.lower() == "p" and row in (0, 7):
                options = ["Queen", "Rook", "Bishop", "Knight"]

                selected_option, accepted = QInputDialog.getItem(
                    self,
                    "Pawn promotion",
                    "Promote pawn to:",
                    options,
                    0,
                    False
                )

                if not accepted:
                    return

                promotion_symbols = {
                    "Queen": "q",
                    "Rook": "r",
                    "Bishop": "b",
                    "Knight": "n"
                }

                promotion_choice = promotion_symbols[selected_option]

            self.game.make_move(
                start_row,
                start_col,
                row,
                col,
                promotion_choice
            )

            self.selected = None
            self.selected_moves = []

            self.refresh_board()
            self.update_game_status()

            
            if not self.game_over:
                QTimer.singleShot(500, self.run_bot_turn)

            return

        # Deselect the selected piece
        if self.selected == (row, col):
            self.selected = None
            self.selected_moves = []

            self.refresh_board()
            return

        # Do nothing when an unhighlighted empty square is clicked
        if piece == "-":
            return
        
        # Prevent the player from selecting the opponent's piece
        if not validate_player_move(self.game.current_p, piece):
            print(f"It is {self.game.current_p}'s turn")
            return

        # Select a piece
        self.selected = (row, col)

        piece_object = create_piece_object(piece, self.game.current_p)

        self.selected_moves = self.game.get_legal_moves(
            self.game.current_p,
            row,
            col,
            piece_object
        )

        print("Selected:", self.selected)
        print("Piece:", piece)
        print("Valid moves:", self.selected_moves)

        self.refresh_board()
