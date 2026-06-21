import sys
import os

from PySide6.QtWidgets import (
    QApplication,
    QInputDialog,
    QGridLayout,
    QMainWindow,
    QPushButton,
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget
)

from pathlib import Path

from PySide6.QtCore import QSize, QTimer, Qt, QProcess
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
        self.last_move = None
        self.move_history = []

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

        main_layout = QHBoxLayout()
        board_layout = QGridLayout()
        side_layout = QVBoxLayout()

        board_layout.setSpacing(0)
        board_layout.setContentsMargins(20, 20, 20, 20)


        for row in range(8):
            button_row = []

            for col in range(8):
                # create buttons
                block = QPushButton()
                block.setMinimumSize(100, 110)
                block.setIconSize(QSize(75, 75))

                block.clicked.connect(
                    lambda checked=False, display_row=row, display_col=col:
                    self.handle_square_click(
                        *self.display_to_board(display_row, display_col)
                    )
                )

                # add widgets to grid and buttons to list
                board_layout.addWidget(block, row+1, col+1)
                button_row.append(block)

            self.buttons.append(button_row)

        if self.human_player == "black":
            files = ["H", "G", "F", "E", "D", "C", "B", "A"]
            ranks = ["1", "2", "3", "4", "5", "6", "7", "8"]
        else:
            files = ["A", "B", "C", "D", "E", "F", "G", "H"]
            ranks = ["8", "7", "6", "5", "4", "3", "2", "1"]

        # Top file labels
        for col in range(8):
            label = self.create_coordinate_label(files[col])
            board_layout.addWidget(label, 0, col + 1)

        # Bottom file labels
        for col in range(8):
            label = self.create_coordinate_label(files[col])
            board_layout.addWidget(label, 9, col + 1)

        # Left rank labels
        for row in range(8):
            label = self.create_coordinate_label(ranks[row])
            board_layout.addWidget(label, row + 1, 0)

        # Right rank labels
        for row in range(8):
            label = self.create_coordinate_label(ranks[row])
            board_layout.addWidget(label, row + 1, 9)

        history_title = QLabel("Move History")
        history_title.setAlignment(Qt.AlignCenter)
        history_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: white;
                padding: 10px;
            }
        """)

        self.history_list = QListWidget()
        self.history_list.setMinimumWidth(220)
        self.history_list.setStyleSheet("""
            QListWidget {
                font-size: 16px;
                background-color: #2E2E2E;
                color: white;
                border: 2px solid #5D4037;
                padding: 5px;
            }
        """)

        side_layout.addWidget(history_title)
        side_layout.addWidget(self.history_list)

        restart_button = QPushButton("Restart Game")
        restart_button.setMinimumHeight(45)
        restart_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #FBC02D;
                color: black;
                border: none;
                padding: 8px;
            }

            QPushButton:hover {
                background-color: #FDD835;
            }
        """)

        restart_button.clicked.connect(self.restart_game)

        quit_button = QPushButton("Quit")
        quit_button.setMinimumHeight(45)
        quit_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #B71C1C;
                color: white;
                border: none;
                padding: 8px;
            }

            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)

        quit_button.clicked.connect(QApplication.quit)

        side_layout.addWidget(restart_button)
        side_layout.addWidget(quit_button)

        main_layout.addLayout(board_layout)
        main_layout.addLayout(side_layout)

        main_container.setLayout(main_layout)
        self.setCentralWidget(main_container)

        self.refresh_board()
        self.update_game_status()

        # The white bot must make the opening move
        if self.bot_player == "white":
            QTimer.singleShot(500, self.run_bot_turn)
            

    def add_move_to_history(self, player, start_row, start_col, end_row, end_col):
        from_square = convert_to_chess_notation(start_row, start_col)
        to_square = convert_to_chess_notation(end_row, end_col)

        move_text = f"{player.capitalize()}: {from_square} → {to_square}\n"

        self.move_history.append(move_text)

        self.history_list.clear()

        move_number = 1

        for i in range(0, len(self.move_history), 2):
            white_move = self.move_history[i]

            if i + 1 < len(self.move_history):
                black_move = self.move_history[i + 1]
                display_text = f"{move_number}. {white_move}    {black_move}"
            else:
                display_text = f"{move_number}. {white_move}"

            self.history_list.addItem(display_text)
            move_number += 1

        self.history_list.scrollToBottom()


    def create_coordinate_label(self, text):
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)

        label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
                padding: 20px;
            }
        """)
        return label
    
    def display_to_board(self, display_row, display_col):
        if self.human_player == "black":
            return 7 - display_row, 7 - display_col

        return display_row, display_col
    

    def refresh_board(self):

        self.setWindowTitle(
            f"Chess - {self.human_player.capitalize()} vs "
            f"{self.bot_difficulty.capitalize()} bot - "
            f"{self.game.current_p.capitalize()}'s turn"
        )

        checked_king = None

        if self.game.is_in_check(self.game.current_p):
            checked_king = self.game.find_king(self.game.current_p)

        for display_row in range(8):
            for display_col in range(8):
                board_row, board_col = self.display_to_board(
                    display_row,
                    display_col
                )

                button = self.buttons[display_row][display_col]
                piece = self.game.board[board_row][board_col]

                # Remove the previous icon
                button.setIcon(QIcon())

                if piece != "-":
                    image_path = ASSETS_PATH / piece_images[piece]
                    button.setIcon(QIcon(str(image_path)))

                # King currently in check
                if checked_king == (board_row, board_col):
                    colour = "#E53935"

                # Highlight the selected square
                elif self.selected == (board_row, board_col):
                    colour = "#FDD835"

                # Highlight the previous move
                elif self.last_move is not None and (board_row, board_col) in self.last_move:
                    colour = "#FBC02D"

                # Valid destination
                elif (board_row, board_col) in self.selected_moves:
                    colour = "#66BB6A"

                # Normal board colours based on visible square position
                elif (display_row + display_col) % 2 == 0:
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

        moving_player = self.game.current_p
        last_move = perform_bot_turn(self.game, self.bot_difficulty)

        start_row, start_col = last_move[0]
        end_row, end_col = last_move[1]

        self.add_move_to_history(moving_player, start_row, start_col, end_row, end_col)

        if last_move is not None:
            self.last_move = last_move

        self.refresh_board()
        self.update_game_status()


    def restart_game(self):
        QProcess.startDetached(
            sys.executable,
            sys.argv,
            os.getcwd()
        )

        QApplication.quit()


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

            moving_player = self.game.current_p

            self.game.make_move(start_row, start_col, row, col, promotion_choice)

            self.add_move_to_history(moving_player, start_row, start_col, row, col)

            self.last_move = [(start_row, start_col),(row, col)]

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
