from board import *
from game import *
from move_validator import *
from pieces import *
from player import *
from utils import *

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