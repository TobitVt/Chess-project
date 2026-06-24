from database import connect

DEFAULT_ELO = 200


def get_starting_elo(player_elo):
    return player_elo if player_elo and player_elo > 0 else DEFAULT_ELO


def calculate_expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400.0))


def calculate_elo_change(rating_a, rating_b, actual_score, k_factor=24):
    expected_score = calculate_expected_score(rating_a, rating_b)
    return int(round(k_factor * (actual_score - expected_score)))


def update_player_rating(player_id, new_elo, result):
    conn = connect()
    cursor = conn.cursor()

    if result == "win":
        cursor.execute(
            """
            UPDATE players
            SET elo = ?, wins = wins + 1
            WHERE player_id = ?
            """,
            (new_elo, player_id)
        )

    elif result == "draw":
        cursor.execute(
            """
            UPDATE players
            SET elo = ?, draws = draws + 1
            WHERE player_id = ?
            """,
            (new_elo, player_id)
        )

    else:
        cursor.execute(
            """
            UPDATE players
            SET elo = ?, losses = losses + 1
            WHERE player_id = ?
            """,
            (new_elo, player_id)
        )

    conn.commit()
    conn.close()


def apply_game_result_elo(chess_game, result, human_player, human_player_id):
    if result is None or human_player is None or human_player_id is None:
        return None

    human_color = None

    for color, player in chess_game.players.items():
        if player is human_player:
            human_color = color
            break

    if human_color is None:
        return None

    opponent_color = "black" if human_color == "white" else "white"
    opponent_player = chess_game.players[opponent_color]

    human_rating = getattr(human_player, "elo", DEFAULT_ELO)
    opponent_rating = getattr(opponent_player, "elo", DEFAULT_ELO)

    if result["outcome"] == "draw":
        actual_score = 0.5
        outcome = "draw"

    else:
        winner = result.get("winner")

        if winner == human_color:
            actual_score = 1.0
            outcome = "win"
        else:
            actual_score = 0.0
            outcome = "loss"

    elo_change = calculate_elo_change(human_rating, opponent_rating, actual_score)

    new_rating = human_rating + elo_change

    update_player_rating(human_player_id, new_rating, outcome)

    if hasattr(human_player, "update_elo"):
        human_player.update_elo(new_rating)
    else:
        human_player.elo = new_rating

    return {
        "new_elo": new_rating,
        "elo_change": elo_change,
        "outcome": outcome
    }