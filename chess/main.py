from board import *
from move_validator import *
from pieces import *
from player import *
from utils import *
from database import *
from login import *

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

player1 = Player(f"{logged_in_player['username']} / white")
player2 = Player("Bot / black")

chess_game = Game(chess_board, player1, player2)

window = ChessBoard(chess_game, logged_in_player)
window.show()

sys.exit(app.exec())


# done: # log in/sign up, timer, create pop up for game end reason, captured list with icons, update ReadMe