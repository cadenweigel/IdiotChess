import random
from app.player import Player
from app.board import Board

class IdiotBot(Player):
    def __init__(self, name: str, color: str, image: str = None):
        super().__init__(name, color, image)

    def decide_move(self, board: Board):
        """
        Picks a random valid move from all available options.
        Returns a tuple: (from_position, to_position)
        """
        all_moves = []

        for row in range(8):
            for col in range(8):
                piece = board.get_piece_at((row, col))
                if piece and piece.color == self.color:
                    for move in piece.get_valid_moves(board):
                        all_moves.append(((row, col), move))

        return random.choice(all_moves) if all_moves else None
