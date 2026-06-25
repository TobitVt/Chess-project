import sys

from PySide6.QtWidgets import QApplication, QDialog

from board import create_board
from player import Player
from database import create_tables, load_saved_game
from login import LoginDialog
from main_menu import MainMenuDialog
from elo import get_starting_elo, DEFAULT_ELO
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

loaded_game = None

# Load saved game if selected
if (game_settings["mode"] == "bot" and game_settings.get("new_load") == "load"):
    loaded_game = load_saved_game(game_settings["save_id"])


# Create board and restore saved settings if needed
if loaded_game is not None:
    chess_board = loaded_game["board"]

    bot_colour = loaded_game["bot_color"] or "black"

    game_settings["bot_colour"] = bot_colour
    game_settings["human_colour"] = ("black" if bot_colour == "white" else "white")

    game_settings["bot_difficulty"] = loaded_game["bot_difficulty"]

    game_settings["time_limit_seconds"] = (loaded_game["time_limit_seconds"] if loaded_game["time_limit_seconds"] is not None else 600)

    game_settings["white_time_left"] = (loaded_game["white_time_left"] if loaded_game["white_time_left"] is not None else game_settings["time_limit_seconds"])

    game_settings["black_time_left"] = (loaded_game["black_time_left"] if loaded_game["black_time_left"] is not None else game_settings["time_limit_seconds"])

    game_settings["move_history"] = loaded_game.get("move_history", [])
    game_settings["white_captured_pieces"] = loaded_game.get("white_captured_pieces", [])
    game_settings["black_captured_pieces"] = loaded_game.get("black_captured_pieces", [])

else:
    chess_board = create_board()

    game_settings["white_time_left"] = game_settings["time_limit_seconds"]
    game_settings["black_time_left"] = game_settings["time_limit_seconds"]

    game_settings["move_history"] = []
    game_settings["white_captured_pieces"] = []
    game_settings["black_captured_pieces"] = []


username = logged_in_player["username"]
human_elo = logged_in_player["elo"]


# Create players
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


# Restore whose turn it was
if loaded_game is not None:
    chess_game.current_p = loaded_game["current_turn"]


window = ChessBoard(chess_game, logged_in_player, game_settings)

window.show()

sys.exit(app.exec())
