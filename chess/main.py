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


def get_game_mode():
    prompt = "Select mode: user or bot? (user/bot): "
    while True:
        mode = input(prompt).strip().lower()
        if mode in ("user", "u"):
            return "user"
        if mode in ("bot", "b"):
            return "bot"
        print("Please enter 'user' or 'bot'.")


def get_bot_difficulty():
    prompt = "Select bot difficulty (easy/medium/hard): "
    while True:
        difficulty = input(prompt).strip().lower()
        if difficulty in ("easy", "medium", "hard"):
            return difficulty
        print("Please enter 'easy', 'medium', or 'hard'.")


def get_bot_color():
    prompt = "Select bot color (black/white): "
    while True:
        color = input(prompt).strip().lower()
        if color in ("black", "white"):
            return color
        print("Please enter 'black' or 'white'.")


def print_turn_header(game):
    current_color = game.current_p
    if game.is_in_check(current_color):
        print("CHECK! You are in check.")
    print_board(game.board)
    current_player = game.get_current_player()
    print(f"player at turn: {current_player.get_player_info()}")
    print(f"captured pieces: {current_player.get_captured_list()}")


def show_end_game(game, player_color):
    if game.is_checkmate(player_color):
        print_board(game.board)
        print(f"CHECKMATE! {player_color.capitalize()} loses.")
        return True

    if game.is_stalemate(player_color):
        print_board(game.board)
        print("STALEMATE! Draw.")
        return True

    return False


def perform_human_turn(game, timer):
    from_piece = timer.timed_input("what piece do you want to move?: ")
    from_piece = game.validate_from(from_piece, input_func=timer.timed_input)
    to_piece = timer.timed_input("where should the piece go?: ")
    to_piece = game.validate_to(to_piece, input_func=timer.timed_input)
    elapsed, timed_out = timer.stop_turn()

    if timed_out:
        return None, True

    game.make_move(from_piece, to_piece)
    return elapsed, False




def perform_bot_turn(game, timer, difficulty):
    # obtain bot move(s) according to difficulty
    if difficulty == "easy":
        bot_from_move = game.easy_bot_move()
        bot_to_move = game.easyBot_to()

    if difficulty == "medium":
        bot_from_move = game.medBot_from()
        bot_to_move = game.medBot_to()

    if difficulty == "hard":
        bot_from_move = game.hardBot_from()
        bot_to_move = game.hardBot_to()


    # if bot_from_move returned a (from,to) tuple, unpack it
    if isinstance(bot_from_move, tuple):
        from_piece, to_piece = bot_from_move
    else:
        from_piece = bot_from_move
        to_piece = bot_to_move

    # validate we have both squares
    if not from_piece or not to_piece:
        timer.stop_turn()
        print("Bot has no legal moves.")
        return None, False

    print(f"Bot chooses {from_piece} to {to_piece}")
    elapsed, timed_out = timer.stop_turn()

    if timed_out:
        return None, True

    game.make_move(from_piece, to_piece)
    return elapsed, False


player1 = Player("Player 1 / white", 0)
player2 = Player("Player 2 / black", 0)

mode = get_game_mode()
bot_difficulty = None
bot_color = None
if mode == "bot":
    bot_difficulty = get_bot_difficulty()
    bot_color = get_bot_color()
    print(f"Bot difficulty set to {bot_difficulty} and bot will play as {bot_color}.")

    if bot_color == "black":
        player1 = Player("Player 1 / white", 0)
        player2 = Player("Bot / black", 0)
    else:
        player1 = Player("Bot / white", 0)
        player2 = Player("Player 1 / black", 0)

chess_game = Game(chess_board, player1, player2)

time_limit = get_time_limit_minutes()
chess_timer = ChessTimer(time_limit)

while True:
    current_color = chess_game.current_p

    # check for game-over before the current turn
    if show_end_game(chess_game, current_color):
        break

    # verify the current player still has time remaining
    if not chess_timer.has_time(current_color):
        print(f"{current_color.capitalize()} ran out of time. Game over.")
        break

    chess_timer.start_turn(current_color)
    print_turn_header(chess_game)

    # select the correct move flow for human or bot play
    if mode == "bot" and current_color == bot_color:
        elapsed, timed_out = perform_bot_turn(chess_game, chess_timer, bot_difficulty)
    else:
        elapsed, timed_out = perform_human_turn(chess_game, chess_timer)

    if timed_out:
        print(f"{current_color.capitalize()} ran out of time! Move not completed.")
        break

    print(f"Move time: {elapsed} seconds | Remaining: {format_time(chess_timer.get_remaining(current_color))}")

    next_color = chess_game.current_p

    # check for game-over after the move has been made
    if show_end_game(chess_game, next_color):
        break
