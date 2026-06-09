#################player representation exercise ###############################
class Player:
    def __init__(self, name, score = 0):
        self.name = name
        self.score = score
        self.elo = score
        self.captured_pieces = []

    def update_score(self, n):
        self.score += int(n)

    def update_elo(self, new_elo):
        self.elo = new_elo
        self.score = new_elo

    def capture_piece(self, piece):
        self.captured_pieces.append(piece)

    def get_captured_list(self):
        return self.captured_pieces

    def get_player_info(self):
        return f"{self.name} - {self.score} points"

