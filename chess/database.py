import sqlite3
import json
import hashlib

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
        bot_color TEXT,
        time_limit_seconds INTEGER,
        player_time_left INTEGER,
        saved_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (player_id) REFERENCES players(player_id)
    )
    """)

    add_column_if_missing(cursor, "saved_games", "white_time_left", "INTEGER")

    add_column_if_missing(cursor, "saved_games", "black_time_left", "INTEGER")

    add_column_if_missing(cursor, "saved_games", "white_time_left", "INTEGER")
    add_column_if_missing(cursor, "saved_games", "black_time_left", "INTEGER")
    add_column_if_missing(cursor, "saved_games", "move_history", "TEXT")
    add_column_if_missing(cursor, "saved_games", "white_captured_pieces", "TEXT")
    add_column_if_missing(cursor, "saved_games", "black_captured_pieces", "TEXT")

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


def save_game(player_id, board, current_turn, bot_difficulty, bot_color=None, time_limit_seconds=None, player_time_left=None, white_time_left=None, black_time_left=None, 
              move_history = None, white_captured_pieces = None, black_captured_pieces = None):
    conn = connect()
    cursor = conn.cursor()

    board_state = json.dumps(board)
    move_history_state = json.dumps(move_history or [])
    white_captured_state = json.dumps(white_captured_pieces or [])
    black_captured_state = json.dumps(black_captured_pieces or [])

    cursor.execute("""
    INSERT INTO saved_games (
        player_id,
        board_state,
        current_turn,
        bot_difficulty,
        bot_color,
        time_limit_seconds,
        player_time_left,
        white_time_left,
        black_time_left,
        move_history,
        white_captured_pieces,
        black_captured_pieces
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        player_id,
        board_state,
        current_turn,
        bot_difficulty,
        bot_color,
        time_limit_seconds,
        player_time_left,
        white_time_left,
        black_time_left,
        move_history_state,
        white_captured_state,
        black_captured_state
    ))

    conn.commit()
    save_id = cursor.lastrowid

    conn.close()
    return save_id

def get_all_saved_games(player_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT save_id, current_turn, bot_difficulty, saved_at
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
    SELECT
        board_state,
        current_turn,
        bot_difficulty,
        bot_color,
        time_limit_seconds,
        player_time_left,
        white_time_left,
        black_time_left,
        move_history,
        white_captured_pieces,
        black_captured_pieces
    FROM saved_games
    WHERE save_id = ?
    """, (save_id,))

    save = cursor.fetchone()
    conn.close()

    if save is None:
        return None

    (
        board_state,
        current_turn,
        bot_difficulty,
        bot_color,
        time_limit_seconds,
        player_time_left,
        white_time_left,
        black_time_left,
        move_history,
        white_captured_pieces,
        black_captured_pieces
    ) = save

    return {
        "board": json.loads(board_state),
        "current_turn": current_turn,
        "bot_difficulty": bot_difficulty,
        "bot_color": bot_color,
        "time_limit_seconds": time_limit_seconds,
        "player_time_left": player_time_left,
        "white_time_left": white_time_left,
        "black_time_left": black_time_left,
        "move_history": json.loads(move_history) if move_history else [],
        "white_captured_pieces": json.loads(white_captured_pieces) if white_captured_pieces else [],
        "black_captured_pieces": json.loads(black_captured_pieces) if black_captured_pieces else []
    }

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_login(u_name, p_word):
    user_info = get_player(u_name)

    if user_info is None:
        return None

    entered_password_hash = hash_password(p_word)
    stored_hashed_password = user_info[2]

    if entered_password_hash != stored_hashed_password:
        return None

    return {
        "player_id": user_info[0],
        "username": user_info[1],
        "elo": user_info[3],
        "wins": user_info[4],
        "losses": user_info[5],
        "draws": user_info[6],
        "is_guest": False
    }

def add_column_if_missing(cursor, table_name, column_name, column_definition):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]

    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")