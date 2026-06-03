import sqlite3
import json

DB_NAME = "chess_game.db"

def connect():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        elo INTEGER DEFAULT 0,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        draws INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saved_games (
        save_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id INTEGER NOT NULL,
        board_state TEXT NOT NULL,
        current_turn TEXT NOT NULL,
        bot_difficulty TEXT,
        game_mode TEXT NOT NULL,
        saved_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (player_id) REFERENCES players(player_id)
    )
    """)

    conn.commit()
    conn.close()

def create_player(u_name, p_word):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO players (username, password) values (?, ?)""", (u_name, p_word))
        conn.commit()
        player_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        conn.close()
        return None
    
    conn.close()
    return player_id


def get_player(u_name):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT player_id, username, password, elo, wins, losses, draws
        FROM players
        WHERE username = ?
        """, (u_name,))

    player = cursor.fetchone()

    conn.close()
    return player


def save_game(player_id, board, current_turn, bot_difficulty, game_mode):
    conn = connect()
    cursor = conn.cursor()

    board_state = json.dumps(board)

    cursor.execute("""
    INSERT INTO saved_games (
        player_id,
        board_state,
        current_turn,
        bot_difficulty,
        game_mode
    )
    VALUES (?, ?, ?, ?, ?)
    """, (player_id, board_state, current_turn, bot_difficulty, game_mode))

    conn.commit()
    save_id = cursor.lastrowid

    conn.close()
    return save_id

def get_all_saved_games(player_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT save_id, current_turn, bot_difficulty, game_mode, saved_at
    FROM saved_games
    WHERE player_id = ?
    ORDER BY saved_at DESC
    """, (player_id,))

    saves = cursor.fetchall()

    conn.close()
    return saves

def load_saved_game(save_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT board_state, current_turn, bot_difficulty, game_mode
    FROM saved_games
    WHERE save_id = ?
    """, (save_id,))

    save = cursor.fetchone()
    conn.close()

    if save is None:
        return None

    board_state, current_turn, bot_difficulty, game_mode = save

    board = json.loads(board_state)

    return {
        "board": board,
        "current_turn": current_turn,
        "bot_difficulty": bot_difficulty,
        "game_mode": game_mode
    }

# create_tables()
# print("Database and tables created successfully.")