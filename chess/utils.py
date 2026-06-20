import sqlite3
from board import *

DEFAULT_ELO = 1200


def get_starting_elo(player_elo):
    return player_elo if player_elo and player_elo > 0 else DEFAULT_ELO


def calculate_expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400.0))


def calculate_elo_change(rating_a, rating_b, actual_score, k_factor=24):
    expected_score = calculate_expected_score(rating_a, rating_b)
    return int(round(k_factor * (actual_score - expected_score)))


def update_player_rating(player_id, new_elo, result, db_name="chess_game.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    if result == "win":
        cursor.execute("UPDATE players SET elo = ?, wins = wins + 1 WHERE player_id = ?", (new_elo, player_id))
    elif result == "draw":
        cursor.execute("UPDATE players SET elo = ?, draws = draws + 1 WHERE player_id = ?", (new_elo, player_id))
    else:
        cursor.execute("UPDATE players SET elo = ?, losses = losses + 1 WHERE player_id = ?", (new_elo, player_id))

    conn.commit()
    conn.close()


def apply_game_result_elo(chess_game, result, human_player, human_player_id, db_name="chess_game.db"):
    if not result or human_player is None or human_player_id is None:
        return None

    human_color = next((color for color, player in chess_game.players.items() if player is human_player), None)
    if human_color is None:
        return None

    opponent_color = "black" if human_color == "white" else "white"
    opponent_player = chess_game.players[opponent_color]

    human_rating = getattr(human_player, "elo", getattr(human_player, "score", DEFAULT_ELO))
    opponent_rating = getattr(opponent_player, "elo", getattr(opponent_player, "score", DEFAULT_ELO))

    if result["outcome"] == "draw":
        actual_score = 0.5
        outcome = "draw"
    elif result["outcome"] == "resign":
        actual_score = 0.0
        outcome = "loss"
    else:
        actual_score = 1.0 if result["winner"] == human_color else 0.0
        outcome = "win" if actual_score == 1.0 else "loss"

    new_rating = human_rating + calculate_elo_change(human_rating, opponent_rating, actual_score)
    update_player_rating(human_player_id, new_rating, outcome, db_name=db_name)
    human_player.update_elo(new_rating)
    print(f"{human_player.name} rating updated to {new_rating} ({outcome}).")
    return new_rating


# chess notation to list index
def convert_move(str_coord):
    str_coord = str_coord.strip().lower()

    # if str_coord = e1:

    # takes e and uses the ord function to change it into a number(a = 96, b = 97, c = 98, etc) 
    # then subtracts ord('a') which is 96 to get the correct row number for list indexes (a = 0, b = 1, c = 2, etc)
    col = ord(str_coord[0].lower()) - ord('a')

    # takes the second char of the coordinates and turns it into a string, subtracting 
    # that from 8 to get the chess board coordinate that corresponds to the list index
    row = 8 - int(str_coord[1])

    if not (0 <= row < 8 and 0 <= col < 8):
       raise ValueError(f"Invalid board coordinate: {str_coord}")

    return (row, col)

# list index to chess notation
def convert_to_chess_notation(row, col):

    file = chr(col + ord('a'))
    rank = str(8 - row)

    return file + rank


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

    from_coord = convert_move(from_piece)
    to_coor = convert_move(to_piece)

    r1, c1 = from_coord

    r2, c2 = to_coor

    game.make_move(r1, c1, r2, c2)

    return [(r1, c1), (r2, c2)]

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

