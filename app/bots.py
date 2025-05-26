import random
from app.player import Player
from app.board import Board
from app.move_scoring import find_best_greedy_move, find_random_move, PIECE_VALUES
from app.position_evaluation import evaluate_position_mobility, evaluate_position_safety
from app.minimax_search import find_best_move

class IdiotBot(Player):
    def __init__(self, name: str = None, color: str = None, image: str = None):
        super().__init__(name=name or "IdiotBot", color=color, image=image)

    def decide_move(self, board: Board):
        """
        Picks a random valid move from all available options.
        When in check, only considers moves that get out of check.
        Returns a tuple: (from_position, to_position) or None if no valid moves (checkmate)
        """
        return find_random_move(board, self.color)

class WhiteIdiotBot(IdiotBot):
    def __init__(self, name: str = None, color: str = None, image: str = None):
        super().__init__(name=name or "Wyatt", color=color or "white", image=image or "wyatt.png")

class BlackIdiotBot(IdiotBot):
    def __init__(self, name: str = None, color: str = None, image: str = None):
        super().__init__(name=name or "Moose", color=color or "black", image=image or "moose.png")

class GreedyBot(Player):
    def __init__(self, name: str = None, color: str = None, image: str = None):
        super().__init__(name=name or "Pongo", color=color, image=image or "pongo.png")

    def decide_move(self, board: Board):
        """
        Picks randomly from the best valid moves based on piece values and captures.
        When in check, only considers moves that get out of check.
        Returns a tuple: (from_position, to_position) or None if no valid moves (checkmate)
        """
        return find_best_greedy_move(board, self.color)

def evaluate_material(board: Board, color: str) -> float:
    """
    Evaluate a position based on material value.
    
    Args:
        board: Current board state
        color: Color of the player to evaluate for
        
    Returns:
        float: Position score (higher is better for the given color)
    """
    score = 0
    opponent_color = 'black' if color == 'white' else 'white'
    
    for row in range(8):
        for col in range(8):
            piece = board.get_piece_at((row, col))
            if piece:
                value = PIECE_VALUES.get(piece.__class__.__name__.lower(), 0)
                if piece.color == color:
                    score += value
                else:
                    score -= value
    
    return score

class MinimaxBot(Player):
    def __init__(self, name: str = None, color: str = None, image: str = None):
        super().__init__(name=name or "Borzoi", color=color, image=image or "borzoi.png")

    def decide_move(self, board: Board):
        """
        Implements a one-ply minimax algorithm to choose the best move.
        Looks one move ahead for both players and chooses the move that leads to
        the best position after the opponent's best response.
        Returns a tuple: (from_position, to_position) or None if no valid moves (checkmate)
        """
        return find_best_move(board, self.color, 1, evaluate_material)

class BetterMinimaxBotOne(MinimaxBot):
    def __init__(self, name: str = None, color: str = None, image: str = None):
        super().__init__(name=name or "Barrow of Monkeys", color=color, image=image or "barrowofmonkeys.png")
    
    def decide_move(self, board: Board):
        """Decide move using 2-ply minimax with alpha-beta pruning."""
        return find_best_move(board, self.color, 2, evaluate_position_mobility)

class BetterMinimaxBotTwo(MinimaxBot):
    def __init__(self, name: str = None, color: str = None, image: str = None):
        super().__init__(name=name or "Gigantopithecus", color=color, image=image or "gigantopithecus.png")
    
    def decide_move(self, board: Board):
        """Decide move using 2-ply minimax with alpha-beta pruning."""
        return find_best_move(board, self.color, 2, evaluate_position_safety) 