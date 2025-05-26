from app.board import Board
from typing import Callable, Tuple, Optional
import random

def minimax_search(
    board: Board,
    depth: int,
    color: str,
    evaluate_position: Callable[[Board, str], float],
    alpha: float = float('-inf'),
    beta: float = float('inf'),
    maximizing_player: bool = True
) -> float:
    """
    Minimax algorithm with alpha-beta pruning.
    
    Args:
        board: Current board state
        depth: Search depth
        color: Color of the maximizing player
        evaluate_position: Function to evaluate a position
        alpha: Alpha value for pruning
        beta: Beta value for pruning
        maximizing_player: Whether the current player is maximizing
        
    Returns:
        float: Best evaluation score
    """
    if depth == 0:
        return evaluate_position(board, color)
    
    if maximizing_player:
        max_eval = float('-inf')
        for row in range(8):
            for col in range(8):
                piece = board.get_piece_at((row, col))
                if piece and piece.color == color:
                    for move in piece.get_valid_moves(board):
                        test_board = board.copy()
                        if test_board.move_piece((row, col), move):
                            eval = minimax_search(test_board, depth - 1, color, evaluate_position, alpha, beta, False)
                            max_eval = max(max_eval, eval)
                            alpha = max(alpha, eval)
                            if beta <= alpha:
                                break
        return max_eval
    else:
        min_eval = float('inf')
        opponent_color = 'black' if color == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = board.get_piece_at((row, col))
                if piece and piece.color == opponent_color:
                    for move in piece.get_valid_moves(board):
                        test_board = board.copy()
                        if test_board.move_piece((row, col), move):
                            eval = minimax_search(test_board, depth - 1, color, evaluate_position, alpha, beta, True)
                            min_eval = min(min_eval, eval)
                            beta = min(beta, eval)
                            if beta <= alpha:
                                break
        return min_eval

def find_best_move(
    board: Board,
    color: str,
    depth: int,
    evaluate_position: Callable[[Board, str], float]
) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """
    Find the best move using minimax search.
    
    Args:
        board: Current board state
        color: Color of the player to move
        depth: Search depth
        evaluate_position: Function to evaluate a position
        
    Returns:
        Optional[Tuple[Tuple[int, int], Tuple[int, int]]]: Best move as (from_pos, to_pos) or None if no valid moves
    """
    if board.is_checkmate(color):
        return None
    
    best_score = float('-inf')
    best_moves = []
    alpha = float('-inf')
    beta = float('inf')
    
    for row in range(8):
        for col in range(8):
            piece = board.get_piece_at((row, col))
            if piece and piece.color == color:
                for move in piece.get_valid_moves(board):
                    test_board = board.copy()
                    if test_board.move_piece((row, col), move):
                        if board.is_in_check(color) and test_board.is_in_check(color):
                            continue
                        
                        # Use minimax search to evaluate the position
                        score = minimax_search(test_board, depth - 1, color, evaluate_position, alpha, beta, False)
                        if score > best_score:
                            best_score = score
                            best_moves = [((row, col), move)]
                        elif score == best_score:
                            best_moves.append(((row, col), move))
    
    return random.choice(best_moves) if best_moves else None 