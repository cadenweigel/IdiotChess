from app.board import Board
from typing import Optional, Tuple
import random

# Standard piece values
PIECE_VALUES = {
    'pawn': 1,
    'knight': 3,
    'bishop': 3,
    'rook': 5,
    'queen': 9,
    'king': 0  # Don't value king captures as they should be handled by check logic
}

def score_move_by_piece_value(board: Board, from_pos: tuple, to_pos: tuple, color: str) -> float:
    """
    Scores a potential move based on various factors.
    
    Args:
        board: The current board state
        from_pos: The starting position (row, col)
        to_pos: The target position (row, col)
        color: The color of the moving player
        
    Returns:
        float: The score for this move. Higher is better.
    """
    score = 0
    
    # Score captures
    target_piece = board.get_piece_at(to_pos)
    if target_piece:
        piece_type = target_piece.__class__.__name__.lower()
        score += PIECE_VALUES.get(piece_type, 0)
    
    # Bonus for moving pieces to center squares
    center_distance = abs(3.5 - to_pos[0]) + abs(3.5 - to_pos[1])
    score += (4 - center_distance) * 0.1
    
    return score 

# TODO: Add more scoring factors here, such as:
    # - Piece development
    # - King safety
    # - Pawn structure
    # - Control of open files
    # - Piece mobility

def find_best_greedy_move(board: Board, color: str) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """
    Find the best move using greedy search based on piece values and captures.
    
    Args:
        board: Current board state
        color: Color of the player to move
        
    Returns:
        Optional[Tuple[Tuple[int, int], Tuple[int, int]]]: Best move as (from_pos, to_pos) or None if no valid moves
    """
    best_score = float('-inf')
    best_moves = []

    # First check if we're in checkmate
    if board.is_checkmate(color):
        return None

    for row in range(8):
        for col in range(8):
            piece = board.get_piece_at((row, col))
            if piece and piece.color == color:
                for move in piece.get_valid_moves(board):
                    # Create a test board to check if this move is valid
                    test_board = board.copy()
                    if test_board.move_piece((row, col), move):
                        # If we're in check, only keep moves that get us out of check
                        if board.is_in_check(color):
                            if test_board.is_in_check(color):
                                continue  # Skip this move as it doesn't get us out of check
                        score = score_move_by_piece_value(board, (row, col), move, color)
                        if score > best_score:
                            best_score = score
                            best_moves = [((row, col), move)]
                        elif score == best_score:
                            best_moves.append(((row, col), move))

    return random.choice(best_moves) if best_moves else None

def find_random_move(board: Board, color: str) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """
    Find a random valid move from all available options.
    When in check, only considers moves that get out of check.
    
    Args:
        board: Current board state
        color: Color of the player to move
        
    Returns:
        Optional[Tuple[Tuple[int, int], Tuple[int, int]]]: Random move as (from_pos, to_pos) or None if no valid moves
    """
    all_moves = []

    # First check if we're in checkmate
    if board.is_checkmate(color):
        return None

    for row in range(8):
        for col in range(8):
            piece = board.get_piece_at((row, col))
            if piece and piece.color == color:
                for move in piece.get_valid_moves(board):
                    # Create a test board to check if this move is valid
                    test_board = board.copy()
                    if test_board.move_piece((row, col), move):
                        # If we're in check, only keep moves that get us out of check
                        if not board.is_in_check(color) or not test_board.is_in_check(color):
                            all_moves.append(((row, col), move))

    return random.choice(all_moves) if all_moves else None