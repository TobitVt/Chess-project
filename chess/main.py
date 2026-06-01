from board import *
from game import *
from move_validator import *
from pieces import *
from player import *
from utils import *
from chess.timer import *


###############  game code: ####################################################


def get_time_limit_minutes():
    choices = {"3": 3, "5": 5, "10": 10, "30": 30}
    prompt = "Select total minutes per player (3/5/10/30): "
    while True:
        value = input(prompt).strip()
        if value in choices:
            return choices[value] * 60
        print("Please choose one of: 3, 5, 10, 30")


player1 = Player("Player 1 / white", 0)
player2 = Player("Player 2 / black", 0)

chess_game = Game(chess_board, player1, player2)

time_limit = get_time_limit_minutes()
chess_timer = ChessTimer(time_limit)

while True:

    curr = chess_game.get_current_player()
    current_color = chess_game.current_p

    if chess_game.is_checkmate(current_color):
        print_board(chess_board)
        print(f"CHECKMATE! {current_color.capitalize()} loses.")
        break

    if chess_game.is_stalemate(current_color):
        print_board(chess_board)
        print("STALEMATE! Draw.")
        break

    if not chess_timer.has_time(current_color):
        print(f"{current_color.capitalize()} ran out of time. Game over.")
        break

    print_board(chess_board)

    if chess_game.is_in_check(current_color):
        print("CHECK! You are in check.")

    print(f"player at turn: {curr.get_player_info()}")
    print(f"captured pieces: {curr.get_captured_list()}")
    print(f"Time remaining: {format_time(chess_timer.get_remaining(current_color))}")

    chess_timer.start_turn(current_color)
    from_piece = chess_timer.timed_input("what piece do you want to move?: ")
    from_piece = chess_game.validate_from(from_piece, input_func=chess_timer.timed_input)

    to_piece = chess_timer.timed_input("where should the piece go?: ")
    to_piece = chess_game.validate_to(to_piece, input_func=chess_timer.timed_input)
    elapsed, timed_out = chess_timer.stop_turn()

    if timed_out:
        print(f"{current_color.capitalize()} ran out of time! Move not completed.")
        break

    chess_game.make_move(from_piece, to_piece)
    print(f"Move time: {elapsed} seconds | Remaining: {format_time(chess_timer.get_remaining(current_color))}")

    enemy = chess_game.current_p

    if chess_game.is_checkmate(enemy):
        print(f"CHECKMATE! {enemy} loses.")
        break

    if chess_game.is_stalemate(enemy):
        print("STALEMATE! Draw.")
        break
