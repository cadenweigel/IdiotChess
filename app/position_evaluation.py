from app.board import Board
from app.move_scoring import score_move_by_piece_value, PIECE_VALUES

# Piece-square tables for positional evaluation
PAWN_PST = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5,  5, 10, 25, 25, 10,  5,  5],
    [0,  0,  0, 20, 20,  0,  0,  0],
    [5, -5,-10,  0,  0,-10, -5,  5],
    [5, 10, 10,-20,-20, 10, 10,  5],
    [0,  0,  0,  0,  0,  0,  0,  0]
]

KNIGHT_PST = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

BISHOP_PST = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]

ROOK_PST = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [5, 10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [0,  0,  0,  5,  5,  0,  0,  0]
]

QUEEN_PST = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [-5,  0,  5,  5,  5,  5,  0, -5],
    [0,  0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
]

KING_PST = [
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [20, 20,  0,  0,  0,  0, 20, 20],
    [20, 30, 10,  0,  0, 10, 30, 20]
]

def get_piece_square_value(piece, position):
    """Get the piece-square table value for a piece at a given position."""
    row, col = position
    if piece.color == 'black':
        row = 7 - row  # Flip the board for black pieces
    
    piece_type = piece.__class__.__name__.lower()
    if piece_type == 'pawn':
        return PAWN_PST[row][col]
    elif piece_type == 'knight':
        return KNIGHT_PST[row][col]
    elif piece_type == 'bishop':
        return BISHOP_PST[row][col]
    elif piece_type == 'rook':
        return ROOK_PST[row][col]
    elif piece_type == 'queen':
        return QUEEN_PST[row][col]
    elif piece_type == 'king':
        return KING_PST[row][col]
    return 0

def evaluate_mobility(board, color):
    """Evaluate mobility (number of legal moves) for a color."""
    mobility = 0
    for row in range(8):
        for col in range(8):
            piece = board.get_piece_at((row, col))
            if piece and piece.color == color:
                mobility += len(piece.get_valid_moves(board))
    return mobility

def evaluate_king_safety(board, color):
    """Evaluate king safety based on surrounding pieces and pawn structure."""
    safety = 0
    king_pos = None
    
    # Find king position
    for row in range(8):
        for col in range(8):
            piece = board.get_piece_at((row, col))
            if piece and piece.color == color and piece.__class__.__name__ == 'King':
                king_pos = (row, col)
                break
        if king_pos:
            break
    
    if not king_pos:
        return 0
    
    # Check surrounding squares for friendly pieces
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            check_pos = (king_pos[0] + dr, king_pos[1] + dc)
            if board.is_within_bounds(check_pos):
                piece = board.get_piece_at(check_pos)
                if piece and piece.color == color:
                    safety += 1
    
    # Penalize if king is in check
    if board.is_in_check(color):
        safety -= 3
    
    return safety

def evaluate_material_and_position(board, color):
    """Evaluate material and piece-square table values."""
    score = 0
    for row in range(8):
        for col in range(8):
            piece = board.get_piece_at((row, col))
            if piece:
                value = PIECE_VALUES.get(piece.__class__.__name__.lower(), 0)
                pst_value = get_piece_square_value(piece, (row, col))
                if piece.color == color:
                    score += value + pst_value
                else:
                    score -= value + pst_value
    return score

def evaluate_position_mobility(board: Board, color: str) -> float:
    """
    Evaluate a position based on piece mobility and material.
    
    Args:
        board: Current board state
        color: Color of the player to evaluate for
        
    Returns:
        float: Position score (higher is better for the given color)
    """
    score = 0
    opponent_color = 'black' if color == 'white' else 'white'
    
    # Material score
    for row in range(8):
        for col in range(8):
            piece = board.get_piece_at((row, col))
            if piece:
                value = PIECE_VALUES.get(piece.__class__.__name__.lower(), 0)
                if piece.color == color:
                    score += value
                else:
                    score -= value
    
    # Mobility score
    mobility = 0
    opponent_mobility = 0
    
    for row in range(8):
        for col in range(8):
            piece = board.get_piece_at((row, col))
            if piece:
                moves = piece.get_valid_moves(board)
                if piece.color == color:
                    mobility += len(moves)
                else:
                    opponent_mobility += len(moves)
    
    # Combine material and mobility scores
    score += (mobility - opponent_mobility) * 0.1
    
    return score

def evaluate_position_safety(board: Board, color: str) -> float:
    """
    Evaluate a position based on king safety and material.
    
    Args:
        board: Current board state
        color: Color of the player to evaluate for
        
    Returns:
        float: Position score (higher is better for the given color)
    """
    score = 0
    opponent_color = 'black' if color == 'white' else 'white'
    
    # Material score
    for row in range(8):
        for col in range(8):
            piece = board.get_piece_at((row, col))
            if piece:
                value = PIECE_VALUES.get(piece.__class__.__name__.lower(), 0)
                if piece.color == color:
                    score += value
                else:
                    score -= value
    
    # King safety score
    king_safety = 0
    opponent_king_safety = 0
    
    # Find kings
    for row in range(8):
        for col in range(8):
            piece = board.get_piece_at((row, col))
            if piece and piece.__class__.__name__.lower() == 'king':
                # Count pieces defending the king's area
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if 0 <= row + dr < 8 and 0 <= col + dc < 8:
                            defender = board.get_piece_at((row + dr, col + dc))
                            if defender and defender.color == piece.color:
                                if piece.color == color:
                                    king_safety += 1
                                else:
                                    opponent_king_safety += 1
    
    # Combine material and safety scores
    score += (king_safety - opponent_king_safety) * 0.5
    
    return score 