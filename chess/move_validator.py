
############### helper function exercise #######################################

def validate_player_move(player, piece):
    if piece == "-":
        return False
    
    if player == "white" and piece == piece.upper():
        return True
    
    if player == "black" and piece == piece.lower():
        return True
    
    return False



############### rules engine exercise #########################################

def is_valid(move):
    if len(move) != 2:
        return False
    
    move_file, move_rank = move[0].lower(), move[1]
    if move_file not in 'abcdefgh' or move_rank not in '12345678':
        return False
    return True

