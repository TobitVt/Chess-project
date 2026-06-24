from board import *
from move_validator import *
from pieces import *
from player import *
from utils import *
from database import *
from login import *
from main_menu import *
from elo import *

import sys

from PySide6.QtWidgets import QApplication, QDialog

from game import Game
from chess_interface import ChessBoard
from theme import APP_STYLE


###############  game code: ####################################################

create_tables()

app = QApplication(sys.argv)
app.setStyleSheet(APP_STYLE)

login_dialog = LoginDialog()

if login_dialog.exec() != QDialog.Accepted:
    sys.exit()

logged_in_player = login_dialog.player_info

logged_in_player["elo"] = get_starting_elo(logged_in_player["elo"])

main_menu = MainMenuDialog(logged_in_player)

if main_menu.exec() != QDialog.Accepted:
    sys.exit()

game_settings = main_menu.game_settings

username = logged_in_player["username"]
human_elo = logged_in_player["elo"]

if game_settings["mode"] == "bot":

    if game_settings["bot_colour"] == "black":
        player1 = Player(f"{username} / white", human_elo)
        player2 = Player("Bot / black", DEFAULT_ELO)

    else:
        player1 = Player("Bot / white", DEFAULT_ELO)
        player2 = Player(f"{username} / black", human_elo)
else:
    player1 = Player(f"{username} / white", human_elo)
    player2 = Player("Player 2 / black", DEFAULT_ELO)

chess_game = Game(chess_board, player1, player2)

window = ChessBoard(chess_game, logged_in_player, game_settings)
window.show()

sys.exit(app.exec())
