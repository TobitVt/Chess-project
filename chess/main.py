# 1. main.py (Entry Point)
# Role

# Controls game loop and user interaction.

# Inputs
# User moves (e.g., "e2 e4")

# Outputs
# Calls game logic
# Displays board and results

# Concepts
# Control flow (loops)
# Input/output
# Basic orchestration

# Done When
# You can start the program and it doesn’t crash
# It calls game.py correctly

# Practice Exercise
# Build a loop that:
# Asks for input
# Prints it back
# Exits on "quit"

# main.py
#   ↓
# game.py
#   ↓
# board.py ↔ pieces.py
#   ↓
# move_validator.py
#   ↓
# utils.py

# Phase 1 (Foundation)
# board.py
# utils.py
###############  game code: ####################################################

player1 = Player("Player 1 / white", 0)
player2 = Player("Player 2 / black", 0)


# timeLimit = 60* (int(input("Please select the time limit for each player(5/10/20/30)min: ")))

# timers = {
#     "p1": timeLimit,
#     "p2": timeLimit
# }


chess_game = Game(chess_board, player1, player2)


while True:

    clear_highlights(chess_board)

    curr = chess_game.get_current_player()

    print_board(chess_board)

    print(f"player at turn: {curr.get_player_info()}")
    print(f"captured pieces: {curr.get_captured_list()}")

    # get piece to move from current player and validate move
    from_piece = input("what piece do you want to move?: ")
    from_piece = chess_game.validate_from(from_piece)


    # prompt player to pick where to move piece and validate move
    to_piece = input("where should the piece go?: ")
    to_piece = chess_game.validate_to(to_piece)

    # if move is valid, make move and prepare board for next players move
    chess_game.make_move(from_piece, to_piece)

    enemy = chess_game.current_p

    if chess_game.is_checkmate(enemy):
        print(f"CHECKMATE! {enemy} loses.")
        break

    if chess_game.is_stalemate(enemy):
        print("STALEMATE! Draw.")
        break