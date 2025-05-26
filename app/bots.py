import random
from app.player import Player
from app.board import Board
from app.move_scoring import score_move_by_piece_value, find_best_greedy_move, find_random_move
from app.position_evaluation import evaluate_position_mobility, evaluate_position_safety
from app.minimax_search import find_best_move

class IdiotBot(Player):
    def __init__(self, name: str, color: str, image: str = None):
        super().__init__(name, color, image)

    def decide_move(self, board: Board):
        """
        Picks a random valid move from all available options.
        When in check, only considers moves that get out of check.
        Returns a tuple: (from_position, to_position) or None if no valid moves (checkmate)
        """
        return find_random_move(board, self.color)

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
        return find_best_greedy_move(board, self.color)

class MinimaxBot(Player):
    def __init__(self, name: str, color: str, image: str = None):
        super().__init__(name="Borzoi", color=color, image="borzoi.png")

    def decide_move(self, board: Board):
        """
        Implements a one-ply minimax algorithm to choose the best move.
        Looks one move ahead for both players and chooses the move that leads to
        the best position after the opponent's best response.
        Returns a tuple: (from_position, to_position) or None if no valid moves (checkmate)
        """
        return find_best_move(board, self.color, 1, score_move_by_piece_value)

class BetterMinimaxBotOne(MinimaxBot):
    def __init__(self, name: str, color: str, image: str = None):
        super().__init__(name="Barrow of Monkeys", color=color, image="barrowofmonkeys.png")
    
    def decide_move(self, board: Board):
        """Decide move using 2-ply minimax with alpha-beta pruning."""
        return find_best_move(board, self.color, 2, evaluate_position_mobility)

class BetterMinimaxBotTwo(MinimaxBot):
    def __init__(self, name: str, color: str, image: str = None):
        super().__init__(name="Gigantopithecus", color=color, image="gigantopithecus.png")
    
    def decide_move(self, board: Board):
        """Decide move using 2-ply minimax with alpha-beta pruning."""
        return find_best_move(board, self.color, 2, evaluate_position_safety) 