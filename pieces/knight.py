from typing import List, TYPE_CHECKING
from .piece import Piece, Position

if TYPE_CHECKING:
    from app.board import Board  # Only for type hints

class Knight(Piece):
    """Represents a knight in a game of chess."""

    def get_valid_moves(self, board: 'Board') -> List[Position]:
        """
        Get all valid L-shaped moves for the knight.

        :param board: The game board
        :return: List of valid positions to which the knight can move
        """
        moves: List[Position] = []

        if self.position is None:
            return moves

        row, col = self.position

        # All 8 possible L-shaped moves
        offsets = [
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2), (1, 2),
            (2, -1), (2, 1),
        ]

        for dr, dc in offsets:
            new_pos = (row + dr, col + dc)
            if not board.is_within_bounds(new_pos):
                continue

            piece_at_dest = board.get_piece_at(new_pos)
            if piece_at_dest is None or piece_at_dest.color != self.color:
                moves.append(new_pos)

        return moves