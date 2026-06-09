import sqlite3

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
