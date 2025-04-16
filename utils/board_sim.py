from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pieces.piece import Position
    from app.board import Board

def simulate_move(board: "Board", from_pos: "Position", to_pos: "Position") -> "Board":
    """
    Simulate a move without full deepcopy or triggering game mechanics like castling.
    Used for checking if a move would leave the king in check.
    """
    new_board = board.__class__()
    new_board.grid = [row[:] for row in board.grid]

    piece = board.get_piece_at(from_pos)
    if piece:
        new_piece = type(piece)(piece.color)
        new_piece.set_position(to_pos)
        new_piece.mark_as_moved()
        new_board.grid[to_pos[0]][to_pos[1]] = new_piece
        new_board.grid[from_pos[0]][from_pos[1]] = None
        new_board.last_move = (from_pos, to_pos)

    return new_board
