import random
from app.player import Player
from app.board import Board
from app.move_scoring import score_move_by_piece_value

class IdiotBot(Player):
    def __init__(self, name: str, color: str, image: str = None):
        super().__init__(name, color, image)

    def decide_move(self, board: Board):
        """
        Picks a random valid move from all available options.
        When in check, only considers moves that get out of check.
        Returns a tuple: (from_position, to_position) or None if no valid moves (checkmate)
        """
        all_moves = []

        # First check if we're in checkmate
        if board.is_checkmate(self.color):
            return None

        for row in range(8):
            for col in range(8):
                piece = board.get_piece_at((row, col))
                if piece and piece.color == self.color:
                    for move in piece.get_valid_moves(board):
                        # Create a test board to check if this move is valid
                        test_board = board.copy()
                        if test_board.move_piece((row, col), move):
                            # If we're in check, only keep moves that get us out of check
                            if not board.is_in_check(self.color) or not test_board.is_in_check(self.color):
                                all_moves.append(((row, col), move))

        return random.choice(all_moves) if all_moves else None

class WhiteIdiotBot(IdiotBot):
    def __init__(self):
        super().__init__(name="Wyatt", color="white")

class BlackIdiotBot(IdiotBot):
    def __init__(self):
        super().__init__(name="Moose", color="black")

class GreedyBot(Player):
    def __init__(self, name: str, color: str, image: str = None):
        super().__init__(name="Pongo", color=color, image="pongo.png")

    def decide_move(self, board: Board):
        """
        Picks randomly from the best valid moves based on piece values and captures.
        When in check, only considers moves that get out of check.
        Returns a tuple: (from_position, to_position) or None if no valid moves (checkmate)
        """
        best_score = float('-inf')
        best_moves = []

        # First check if we're in checkmate
        if board.is_checkmate(self.color):
            return None

        for row in range(8):
            for col in range(8):
                piece = board.get_piece_at((row, col))
                if piece and piece.color == self.color:
                    for move in piece.get_valid_moves(board):
                        # Create a test board to check if this move is valid
                        test_board = board.copy()
                        if test_board.move_piece((row, col), move):
                            # If we're in check, only keep moves that get us out of check
                            if board.is_in_check(self.color):
                                # If we're in check, only keep moves that get us out of check
                                if test_board.is_in_check(self.color):
                                    continue  # Skip this move as it doesn't get us out of check
                            score = score_move_by_piece_value(board, (row, col), move, self.color)
                            if score > best_score:
                                best_score = score
                                best_moves = [((row, col), move)]
                            elif score == best_score:
                                best_moves.append(((row, col), move))

        return random.choice(best_moves) if best_moves else None