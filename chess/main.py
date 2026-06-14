from board import *
from game import *
from move_validator import *
from pieces import *
from player import *
from utils import *
# from chess.timer import *
from database import *


###############  game code: ####################################################


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
    prompt = "select the color the bot should play as(black/white): "
    while True:
        color = input(prompt).strip().lower()
        if color in ("black", "white"):
            return color
        print("please select either black or white.")


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
        winner_color = "black" if player_color == "white" else "white"
        print(f"CHECKMATE! {player_color.capitalize()} loses.")
        return {"outcome": "checkmate", "winner": winner_color}

    if game.is_stalemate(player_color):
        print_board(game.board)
        print("STALEMATE! Draw.")
        return {"outcome": "draw"}

    return None


def perform_human_turn(game):
    from_piece = input("what piece do you want to move?: ")
    from_piece = game.validate_from(from_piece)
    to_piece = input("where should the piece go?: ")
    to_piece = game.validate_to(to_piece)

    game.make_move(from_piece, to_piece)


def perform_bot_turn(game, difficulty):
    # obtain bot move(s) according to difficulty
    if difficulty == "easy":
        bot_from_move, bot_to_move = game.easyBot_move()

    if difficulty == "medium":
        bot_from_move, bot_to_move  = game.medBot_move()

    if difficulty == "hard":
        bot_from_move, bot_to_move = game.hardBot_move()


    # if bot_from_move returned a (from,to) tuple, unpack it
    if isinstance(bot_from_move, tuple):
        from_piece, to_piece = bot_from_move
    else:
        from_piece = bot_from_move
        to_piece = bot_to_move

    # validate we have both squares
    if not from_piece or not to_piece:
        print("Bot has no legal moves.")
        return None

    print(f"Bot chooses {from_piece} to {to_piece}")

    game.make_move(from_piece, to_piece)


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
choice = input("\nlog - log in \n sign - sign up \n guest - continue as guest\n your choice: ").strip().lower()
player_name = ""
player_elo = 0
user_info = None

finished = False
while not finished:
    if choice == "log":
        # if db log in matches:
        # continue to game
        # set user name

        # if not:
        # prompt inputs again
        # suggest sign up
        user, passw = log_in_prompt()
        entered_password_hash = hash_password(passw)

        user_info = get_player(user)


        while user_info is None:
            print("\nuser not found in database")
            
            s = input("\ncontinue to sign up instead? (Y/N): ")
            if s.strip().upper() == "Y":
                choice = "sign"
                break

            print("\nPlease try again:\n")
            user, passw = log_in_prompt()
            entered_password_hash = hash_password(passw)


        if choice == "sign":
            continue

        stored_hashed_passw = user_info[2]

        # user found in DB, check password
        while entered_password_hash != stored_hashed_passw:
            passw = input("password incorrect, please try again: ")
            entered_password_hash = hash_password(passw)

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
        hashed_password = hash_password(passw)

        new_id = create_player(user, hashed_password)

        while new_id is None:
            print("\nplayer already exists, please try again")
            l = input("continue to log in instead? (Y/N): ")
            if l.strip().upper() == "Y":
                choice = "log"
                break

            user, passw = sign_up_prompt()
            hashed_password = hash_password(passw)
            new_id = create_player(user, hashed_password)

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
bot_color = None
load_turn = None
loaded_game = None

# chosen to play against bot, can have saved game
human_player = None
human_player_id = None

if mode == "bot":
    # prompt to load game or start a new game
    new_load = "new"

    # guests will not have saved games, skip choice to load game
    if player_name != "guest":
        new_load = input("Play new game(new) or load existing(load)?: ").strip().lower()

        while new_load not in {"new", "load"}:
            print("Invalid option. Please choose a valid option.")
            new_load = input("Play new game(new) or load existing(load)?: ").strip().lower()

    if new_load == "load" and player_name != "guest":
        saved_games = get_all_saved_games(user_info[0])

        if saved_games:
            print("Saved bot games:")
            for index, save in enumerate(saved_games, start=1):
                loaded = load_saved_game(save[0])
                print(f"{index}. {save[3]} | turn: {loaded['current_turn']} | difficulty: {loaded['bot_difficulty']}")

            num_games = len(saved_games)
            while True:
                try:
                    game_choice = int(input(f"What game do you want to load? (1 - {num_games}): ").strip())
                    if 1 <= game_choice <= num_games:
                        break
                except ValueError:
                    game_choice = None

                print("Please enter a valid number.")

            save_id = saved_games[game_choice - 1][0]
            loaded_game = load_saved_game(save_id)
            chess_board = loaded_game["board"]
            load_turn = loaded_game["current_turn"]
            bot_difficulty = loaded_game["bot_difficulty"]
            bot_color = loaded_game.get("bot_color")

        else:
            print("No saved games found, starting new game.")
            new_load = "new"

    if new_load == "new" or player_name == "guest":
        bot_difficulty = get_bot_difficulty()
        bot_color = get_bot_color()
        print(f"Bot difficulty set to {bot_difficulty} and will be playing as {bot_color}.")

        if bot_color == "black":
            player1 = Player(f"{player_name} / white", get_starting_elo(player_elo))
            player2 = Player("Bot / black")

        elif bot_color == "white":
            player1 = Player("Bot / white")
            player2 = Player(f"{player_name} / black", get_starting_elo(player_elo))

    else:
        if bot_color == "black":
            player1 = Player(f"{player_name} / white", get_starting_elo(player_elo))
            player2 = Player("Bot / black")
        else:
            player1 = Player("Bot / white")
            player2 = Player(f"{player_name} / black", get_starting_elo(player_elo))


# player chooses to play against another player, no saved game logic needed
else:
    player1 = Player(f"{player_name} white", get_starting_elo(player_elo))
    player2 = Player("Player 2 / black")



chess_game = Game(chess_board, player1, player2)
if load_turn is not None:
    chess_game.current_p = load_turn

if player_name != "guest" and user_info is not None:
    human_player = next((player for player in chess_game.players.values() if player_name in player.name), None)
    human_player_id = user_info[0]


while True:
    current_color = chess_game.current_p

    # check for immediate game-over conditions before the next turn
    end_state = show_end_game(chess_game, current_color)
    if end_state is not None:
        apply_game_result_elo(chess_game, end_state, human_player, human_player_id)
        break

    print_turn_header(chess_game)

    # select human or bot move based on current mode and player
    if mode == "bot" and current_color == bot_color:
        perform_bot_turn(chess_game, bot_difficulty)
    else:
        perform_human_turn(chess_game)

    next_color = chess_game.current_p

    # check for game-over conditions after the move
    end_state = show_end_game(chess_game, next_color)
    if end_state is not None:
        apply_game_result_elo(chess_game, end_state, human_player, human_player_id)
        break

    cont = input("continue?(Y/N): ").strip().upper()
    while cont not in {"Y", "N"}:
        print("Invalid option. Please choose a valid option.")
        cont = input("save game?(Y/N): ").strip().upper()

    if cont == "N":
        if mode == "bot":
            # guest cant save game, just exit game
            if player_name == "guest":
                print("goodbye!")
                break

            # prompt to save game
            q_save = input("save game?(Y/N): ").strip().upper()
            while q_save not in {"Y", "N"}:
                print("Invalid option. Please choose a valid option.")
                q_save = input("save game?(Y/N): ").strip().upper()

            # stores current board and required info
            if q_save == "Y":
                save_id = save_game(
                    player_id=user_info[0],
                    board=chess_game.board,
                    current_turn=chess_game.current_p,
                    bot_difficulty=bot_difficulty,
                    bot_color=bot_color,
                    time_limit_seconds=0,
                    player_time_left=0,
                )
                print(f"Game saved. Save ID: {save_id}, goodbye!")
                break
            else:
                print("exiting without saving, goodbye!")
                break
        
        elif mode == "player":
            draw_offer = input("Offer a draw? (Y/N): ").strip().upper()
            while draw_offer not in {"Y", "N"}:
                print("Invalid option. Please choose a valid option.")
                draw_offer = input("Offer a draw? (Y/N): ").strip().upper()

            if draw_offer == "Y":
                print("Draw accepted. No rating changes were made.")
                break

            resign = input("Resign and end the game? (Y/N): ").strip().upper()
            while resign not in {"Y", "N"}:
                print("Invalid option. Please choose a valid option.")
                resign = input("Resign and end the game? (Y/N): ").strip().upper()

            if resign == "Y":
                if human_player is not None and human_player_id is not None:
                    losing_color = chess_game.current_p
                    winning_color = "black" if losing_color == "white" else "white"
                    result = {"outcome": "resign", "winner": winning_color}
                    apply_game_result_elo(chess_game, result, human_player, human_player_id)
                print("You resigned. Game over.")
                break

            print("Continuing the game.")
