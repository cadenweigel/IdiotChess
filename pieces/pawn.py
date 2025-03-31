from typing import List, TYPE_CHECKING
from .piece import Piece, Position

if TYPE_CHECKING:
    from app.board import Board  # Only for type hints

class Pawn(Piece):

def get_valid_moves(self, board: 'Board') -> List[Position]:
    moves: List[Position] = []

    if self.position is None:
        return moves

    row, col = self.position
    direction = -1 if self.color == 'white' else 1

    # Forward one step
    one_step = (row + direction, col)
    if board.is_within_bounds(one_step) and board.is_empty(one_step):
        moves.append(one_step)

        # Forward two steps from start row
        start_row = 6 if self.color == 'white' else 1
        two_step = (row + 2 * direction, col)
        if row == start_row and board.is_empty(two_step):
            moves.append(two_step)

    # Diagonal captures
    for dc in [-1, 1]:  # Left and right diagonals
        diag = (row + direction, col + dc)
        if board.is_within_bounds(diag):
            target = board.get_piece_at(diag)
            if target and target.color != self.color:
                moves.append(diag)

    return moves

    def symbol(self) -> str:
        return 'P' if self.color == 'white' else 'p'


    def can_attack(self, target: Position, board: 'Board') -> bool:
        if self.position is None:
            return False

        row, col = self.position
        direction = -1 if self.color == 'white' else 1
        target_row, target_col = target

        return (
            abs(target_col - col) == 1 and
            (target_row - row) == direction and
            board.get_piece_at(target) is not None and
            board.get_piece_at(target).color != self.color
        )