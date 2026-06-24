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
    QListWidget,
    QMessageBox,
    QListWidgetItem
)

from pathlib import Path

from PySide6.QtCore import QSize, QTimer, Qt, QProcess
from PySide6.QtGui import QIcon

from pieces import create_piece_object

from move_validator import *
from utils import *
from elo import *

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
    def __init__(self, game, logged_in_player, game_settings):
        super().__init__()

        self.game = game

        self.logged_in_player = logged_in_player
        self.player_id = logged_in_player["player_id"]
        self.username = logged_in_player["username"]
        self.is_guest = logged_in_player["is_guest"]

        self.game_settings = game_settings

        self.game_mode = game_settings["mode"]
        self.human_player = game_settings["human_colour"]
        self.bot_player = game_settings["bot_colour"]
        self.bot_difficulty = game_settings["bot_difficulty"]

        self.time_limit_seconds = game_settings["time_limit_seconds"]
        self.white_time_left = self.time_limit_seconds
        self.black_time_left = self.time_limit_seconds

        self.buttons = []
        self.selected = None
        self.selected_moves = []
        self.last_move = None
        self.move_history = []

        self.white_captured_pieces = []
        self.black_captured_pieces = []

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_chess_clock)

        self.game_over = False
        self.game_end_popup_shown = False
        self.elo_applied = False

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

                block.clicked.connect(lambda checked=False, display_row=row, display_col=col:
                    self.handle_square_click(*self.display_to_board(display_row, display_col)))

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

        self.profile_label = QLabel()

        self.profile_label.setAlignment(Qt.AlignCenter)
        self.profile_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: white;
                background-color: #2E2E2E;
                border: 2px solid #5D4037;
                padding: 10px;
            }
        """)

        self.update_profile_label()

        side_layout.addWidget(self.profile_label)

        timer_title = QLabel("Timers")
        timer_title.setAlignment(Qt.AlignCenter)
        timer_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: white;
                padding: 10px;
            }
        """)

        self.white_timer_label = QLabel()
        self.black_timer_label = QLabel()

        timer_label_style = """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
                background-color: #2E2E2E;
                border: 2px solid #5D4037;
                padding: 8px;
            }
        """

        self.white_timer_label.setStyleSheet(timer_label_style)
        self.black_timer_label.setStyleSheet(timer_label_style)

        self.white_timer_label.setAlignment(Qt.AlignCenter)
        self.black_timer_label.setAlignment(Qt.AlignCenter)

        side_layout.addWidget(timer_title)
        side_layout.addWidget(self.white_timer_label)
        side_layout.addWidget(self.black_timer_label)

        captured_title = QLabel("Captured Pieces")
        captured_title.setAlignment(Qt.AlignCenter)
        captured_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: white;
                padding: 10px;
            }
        """)

        white_captured_label = QLabel("White captured")
        black_captured_label = QLabel("Black captured")

        white_captured_label.setAlignment(Qt.AlignCenter)
        black_captured_label.setAlignment(Qt.AlignCenter)

        label_style = """
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: white;
            }
        """

        white_captured_label.setStyleSheet(label_style)
        black_captured_label.setStyleSheet(label_style)

        self.white_captured_list = QListWidget()
        self.black_captured_list = QListWidget()

        captured_list_style = """
            QListWidget {
                font-size: 14px;
                background-color: #2E2E2E;
                color: white;
                border: 2px solid #5D4037;
                padding: 4px;
            }
        """

        self.white_captured_list.setStyleSheet(captured_list_style)
        self.black_captured_list.setStyleSheet(captured_list_style)

        self.white_captured_list.setIconSize(QSize(28, 28))
        self.black_captured_list.setIconSize(QSize(28, 28))

        self.white_captured_list.setMaximumHeight(120)
        self.black_captured_list.setMaximumHeight(120)

        side_layout.addWidget(captured_title)
        side_layout.addWidget(white_captured_label)
        side_layout.addWidget(self.white_captured_list)
        side_layout.addWidget(black_captured_label)
        side_layout.addWidget(self.black_captured_list)

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
        self.update_timer_labels()

        self.clock_timer.start(1000)

        # The white bot must make the opening move
        if self.game_mode == "bot" and self.bot_player == "white":
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

        if self.game_mode == "bot":
            title_mode = (f"{self.human_player.capitalize()} vs "f"{self.bot_difficulty.capitalize()} bot")
        else:
            title_mode = "Player vs Player"

        self.setWindowTitle(f"Chess - {title_mode} - "f"{self.game.current_p.capitalize()}'s turn")

        checked_king = None

        if self.game.is_in_check(self.game.current_p):
            checked_king = self.game.find_king(self.game.current_p)

        for display_row in range(8):
            for display_col in range(8):
                board_row, board_col = self.display_to_board(display_row, display_col)

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
                        border-radius: 0px;
                        padding: 0px;
                    }}
                """)

    def update_game_status(self):
        player = self.game.current_p
        player_name = player.capitalize()

        in_check = self.game.is_in_check(player)
        has_legal_moves = self.game.has_any_legal_moves(player)

        if in_check and not has_legal_moves:
            winner = "Black" if player == "white" else "White"
            winner_color = winner.lower()

            message = f"Checkmate! {winner} wins."

            result = {
                "outcome": "checkmate",
                "winner": winner_color
            }

            elo_message = self.apply_elo_result(result)

            popup_message = message

            if elo_message is not None:
                popup_message += f"\n\n{elo_message}"

            self.statusBar().showMessage(message)

            self.game_over = True

            if hasattr(self, "clock_timer"):
                self.clock_timer.stop()

            self.show_game_end_popup("Game Over", popup_message)

        elif not in_check and not has_legal_moves:
            message = "Stalemate! The game is a draw."

            result = {
                "outcome": "draw",
                "winner": None
            }

            elo_message = self.apply_elo_result(result)

            popup_message = message

            if elo_message is not None:
                popup_message += f"\n\n{elo_message}"

            self.statusBar().showMessage(message)

            self.game_over = True

            if hasattr(self, "clock_timer"):
                self.clock_timer.stop()

            self.show_game_end_popup("Game Over", popup_message)

        elif in_check:
            self.statusBar().showMessage(f"{player_name} is in check!")

        else:
            self.statusBar().showMessage(f"{player_name}'s turn")

    def run_bot_turn(self):
        if self.game_over:
            return

        if self.game_mode != "bot":
            return

        if self.game.current_p != self.bot_player:
            return

        moving_player = self.game.current_p

        last_move = perform_bot_turn(self.game, self.bot_difficulty)

        if last_move is None:
            self.refresh_board()
            self.update_game_status()
            self.update_timer_labels()
            return

        self.last_move = last_move

        start_row, start_col = last_move[0]
        end_row, end_col = last_move[1]

        self.add_move_to_history(moving_player, start_row, start_col, end_row, end_col)

        captured_piece = self.game.last_captured_piece

        self.add_captured_piece(moving_player, captured_piece)

        self.refresh_board()
        self.update_game_status()
        self.update_timer_labels()


    def restart_game(self):
        QProcess.startDetached(sys.executable, sys.argv, os.getcwd())

        QApplication.quit()


    def handle_square_click(self, row, col):
        if self.game_over:
            return  
        
        if self.game_mode == "bot" and self.game.current_p == self.bot_player:
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

                selected_option, accepted = QInputDialog.getItem(self, "Pawn promotion", "Promote pawn to:", options, 0, False)

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

            captured_piece = self.game.last_captured_piece

            self.add_captured_piece(moving_player, captured_piece)

            self.add_move_to_history(moving_player, start_row, start_col, row, col)

            self.last_move = [(start_row, start_col),(row, col)]

            self.selected = None
            self.selected_moves = []

            self.refresh_board()
            self.update_game_status()
            self.update_timer_labels()

            
            if (self.game_mode == "bot" and not self.game_over and self.game.current_p == self.bot_player):
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

    def format_time(self, seconds):
        seconds = max(0, seconds)

        minutes = seconds // 60
        remaining_seconds = seconds % 60

        return f"{minutes:02d}:{remaining_seconds:02d}"


    def update_timer_labels(self):
        white_marker = "▶ " if self.game.current_p == "white" else ""
        black_marker = "▶ " if self.game.current_p == "black" else ""

        self.white_timer_label.setText(f"{white_marker}White: {self.format_time(self.white_time_left)}")

        self.black_timer_label.setText(f"{black_marker}Black: {self.format_time(self.black_time_left)}")


    def update_chess_clock(self):
        if self.game_over:
            self.clock_timer.stop()
            return

        if self.game.current_p == "white":
            self.white_time_left -= 1

            if self.white_time_left <= 0:
                self.white_time_left = 0
                self.game_over = True
                self.clock_timer.stop()
                self.selected = None
                self.selected_moves = []
                self.update_timer_labels()
                self.refresh_board()
                
                message = "White ran out of time. Black wins!"

                result = {
                    "outcome": "timeout",
                    "winner": "black"
                }

                elo_message = self.apply_elo_result(result)

                popup_message = message

                if elo_message is not None:
                    popup_message += f"\n\n{elo_message}"

                self.statusBar().showMessage(message)

                self.show_game_end_popup("Time Out", popup_message)
                                
                return

        else:
            self.black_time_left -= 1

            if self.black_time_left <= 0:
                self.black_time_left = 0
                self.game_over = True
                self.clock_timer.stop()
                self.selected = None
                self.selected_moves = []
                self.update_timer_labels()
                self.refresh_board()
                
                message = "Black ran out of time. White wins!"

                result = {
                    "outcome": "timeout",
                    "winner": "white"
                }

                elo_message = self.apply_elo_result(result)

                popup_message = message

                if elo_message is not None:
                    popup_message += f"\n\n{elo_message}"

                self.statusBar().showMessage(message)

                self.show_game_end_popup("Time Out", popup_message)
                
                return

        self.update_timer_labels()

    def show_game_end_popup(self, title, message):
        if self.game_end_popup_shown:
            return

        self.game_end_popup_shown = True

        QMessageBox.information(self, title, message)

    def get_piece_display_name(self, piece):
        piece_names = {
            "p": "Pawn",
            "r": "Rook",
            "n": "Knight",
            "b": "Bishop",
            "q": "Queen",
            "k": "King"
        }

        colour = "White" if piece.isupper() else "Black"
        name = piece_names[piece.lower()]

        return f"{colour} {name}"


    def add_captured_piece(self, capturing_player, captured_piece):
        if captured_piece is None or captured_piece == "-":
            return

        item = QListWidgetItem(self.get_piece_display_name(captured_piece))

        image_path = ASSETS_PATH / piece_images[captured_piece]
        item.setIcon(QIcon(str(image_path)))

        if capturing_player == "white":
            self.white_captured_pieces.append(captured_piece)
            self.white_captured_list.addItem(item)

        else:
            self.black_captured_pieces.append(captured_piece)
            self.black_captured_list.addItem(item)

    def apply_elo_result(self, result):
        if self.elo_applied:
            return None

        if self.is_guest or self.player_id is None:
            return None

        human_color = self.human_player

        if human_color not in self.game.players:
            return None

        human_player_object = self.game.players[human_color]

        elo_result = apply_game_result_elo(self.game, result, human_player_object, self.player_id)

        if elo_result is None:
            return None

        self.elo_applied = True

        new_elo = elo_result["new_elo"]
        outcome = elo_result["outcome"]
        elo_change = elo_result["elo_change"]

        self.logged_in_player["elo"] = new_elo

        if outcome == "win":
            self.logged_in_player["wins"] += 1
        elif outcome == "draw":
            self.logged_in_player["draws"] += 1
        else:
            self.logged_in_player["losses"] += 1

        if hasattr(self, "update_profile_label"):
            self.update_profile_label()

        if elo_change >= 0:
            return f"Your ELO is now {new_elo} (+{elo_change})."

        return f"Your ELO is now {new_elo} ({elo_change})."
    
    def update_profile_label(self):
        self.profile_label.setText(
            f"Player: {self.username}\n"
            f"ELO: {self.logged_in_player['elo']}\n"
            f"Wins: {self.logged_in_player['wins']}  "
            f"Losses: {self.logged_in_player['losses']}  "
            f"Draws: {self.logged_in_player['draws']}"
        )