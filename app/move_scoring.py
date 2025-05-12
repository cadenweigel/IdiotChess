from app.board import Board

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