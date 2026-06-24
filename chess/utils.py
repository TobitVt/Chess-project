from board import *

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


def perform_bot_turn(game, difficulty):
    # obtain bot move(s) according to difficulty
    if difficulty == "easy":
        bot_from_move, bot_to_move = game.easyBot_move()

    elif difficulty == "medium":
        bot_from_move, bot_to_move  = game.medBot_move()

    elif difficulty == "hard":
        bot_from_move, bot_to_move = game.hardBot_move()


    # if bot_from_move returned a (from,to) tuple, unpack it
    if isinstance(bot_from_move, tuple):
        from_piece, to_piece = bot_from_move
    else:
        from_piece = bot_from_move
        to_piece = bot_to_move

    from_coord = convert_move(from_piece)
    to_coor = convert_move(to_piece)

    r1, c1 = from_coord

    r2, c2 = to_coor

    game.make_move(r1, c1, r2, c2)

    return [(r1, c1), (r2, c2)]


