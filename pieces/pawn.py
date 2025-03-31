from typing import List, TYPE_CHECKING
from .piece import Piece, Position

if TYPE_CHECKING:
    from app.board import Board  # Only for type hints

class Pawn(Piece):

    def get_valid_moves(self, board: 'Board') -> List[Position]:
        """
        Get all valid forward moves for this pawn (excluding captures).
        """
        moves: List[Position] = []

        if self.position is None:
            return moves

        row, col = self.position
        direction = -1 if self.color == 'white' else 1

        # One step forward
        one_step = (row + direction, col)
        if board.is_within_bounds(one_step) and board.is_empty(one_step):
            moves.append(one_step)

            # Two steps from starting position
            start_row = 6 if self.color == 'white' else 1
            two_step = (row + 2 * direction, col)
            if row == start_row and board.is_empty(two_step):
                moves.append(two_step)

        return moves