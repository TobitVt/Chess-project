from board import *
from game import *
from move_validator import *
from pieces import *
from player import *
from utils import *
from chess.timer import *
from chess.database import *


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


def print_menu(game_mode):

    if game_mode == "bot":
        menu = "" \
        "quit - quit without saving" \
        "save - quit and save game"



    elif game_mode == "player":
        menu = "" \
        "resign - quit game" \
        "draw - proposes draw to other player"


    else:
        menu = ""

    return menu

def log_in_prompt():
    u_name = input("welcome back! please enter your username: ")
    p_word = input("please enter your password: ")

    return u_name, p_word

def sign_up_prompt():
    u_name = input("welcome to the chess app. Please enter your name/username: ")
    p_word1 = input("please set a password: ")
    p_word2 = input("please confirm password: ")

    while p_word1 != p_word2:
        print("passwords did not match")
        p_word1 = input("please set a password: ")
        p_word2 = input("please confirm password: ")

    return u_name, p_word1

create_tables()

# log in/ sign up
print("Welcome to chess!\n")
choice = input("\nlog - log in \n sign - sign up \n guest - continue as guest\n").strip().lower()
player_name = ""
player_elo = 0

while True:
    if choice == "log":
        # if db log in matches:
        # continue to game
        # set user name

        # if not:
        # prompt inputs again
        # suggest sign up
        user, passw = log_in_prompt()
        user_info = get_player(user)

        while user_info is None:
            print("\nuser not found in database, please try again:")
            user, passw = log_in_prompt()
            user_info = get_player(user)

            if user_info is None:
                s = input("\ncontinue to sign up instead? (Y/N): ")
                if s.strip().upper() == "Y":
                    choice = "sign"
                    break

        if choice == "sign":
            continue

        # user found in DB
        while passw != user_info[2]:
            passw = input("password incorrect, please try again: ")

        print("log in successful, welcome back.")
        player_name = user_info[1]
        player_elo = user_info[3]
        break
        


    if choice == "sign":
        
        # if db account create succesful:
        # continue to game
        # create db entry and set user name

        # if account already exists:
        # prompt sign up again
        # suggest login

        user, passw = sign_up_prompt()
        new_id = create_player(user, passw)

        while new_id is None:
            print("\nplayer already exists, please try again")
            l = input("continue to sign up instead? (Y/N): ")
            if l.strip().upper() == "N":
                choice = "log"
                break

            user, passw = sign_up_prompt()
            new_id = create_player(user, passw)

        if choice == "log":
            continue

        print("sign up successful, welcome.")
        player_name = user
        break


    if choice == "guest":
        # go straight into being prompted to play against player or bot
        player_name = "guest"
        print("welcome to the chess app, enjoy and good luck.")
        break

    if choice not in {"log", "sign", "guest"}:
        print("Invalid option. Please choose log, sign, or guest.")
        choice = input("\nlog - log in \n sign - sign up \n guest - continue as guest\n").strip().lower()
        continue


print(f"welcome {player_name}")

mode = get_game_mode()
bot_difficulty = None
if mode == "bot":
    bot_difficulty = get_bot_difficulty()
    bot_color = get_bot_color()
    print(f"Bot difficulty set to {bot_difficulty} and will be playing as {bot_color}.")

    if bot_color == "black":
        player1 = Player(f"{player_name} / white", player_elo)
        player2 = Player("Bot / black", 0)

    elif bot_color == "white":
        player1 = Player("bot / white", 0)
        player2 = Player(f"{player_name} / black", player_elo)   

else:
    player1 = Player(f"{player_name} white", player_elo)
    player2 = Player("Player 2 / black", 0)     

chess_game = Game(chess_board, player1, player2)

time_limit = get_time_limit_minutes()
chess_timer = ChessTimer(time_limit)


while True:
    current_color = chess_game.current_p

    # check for immediate game-over conditions before the next turn
    if show_end_game(chess_game, current_color):
        break

    # ensure the current player still has time left
    if not chess_timer.has_time(current_color):
        print(f"{current_color.capitalize()} ran out of time. Game over.")
        break

    chess_timer.start_turn(current_color)
    print_turn_header(chess_game)

    menu = input(print_menu(mode))\
    
    # draw/quit, save/quit

    if mode == "bot":
        pass
    
    elif mode == "player":
        pass

    # select human or bot move based on current mode and player
    if mode == "bot" and current_color == bot_color:
        elapsed, timed_out = perform_bot_turn(chess_game, chess_timer, bot_difficulty)
    else:
        elapsed, timed_out = perform_human_turn(chess_game, chess_timer)

    # stop if the move failed due to timeout
    if timed_out:
        print(f"{current_color.capitalize()} ran out of time! Move not completed.")
        break

    print(f"Move time: {elapsed} seconds | Remaining: {format_time(chess_timer.get_remaining(current_color))}")

    next_color = chess_game.current_p

    # check for game-over conditions after the move
    if show_end_game(chess_game, next_color):
        break

