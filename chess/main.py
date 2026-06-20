from board import *
from move_validator import *
from pieces import *
from player import *
from utils import *
from database import *

import sys

from PySide6.QtWidgets import QApplication

from game import Game
from chess_interface import ChessBoard


###############  game code: ####################################################

create_tables()

player1 = Player("Player 1 / white")
player2 = Player("Player 2 / black")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    chess_game = Game(chess_board, player1, player2)

    window = ChessBoard(chess_game)
    window.show()

    sys.exit(app.exec())

