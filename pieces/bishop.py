from typing import List, TYPE_CHECKING
from .piece import Piece, Position

if TYPE_CHECKING:
    from app.board import Board  # Only for type hints

class Bishop(Piece):
    """Represents a bishop in a game of chess."""

    def get_valid_moves(self, board: 'Board') -> List[Position]:
        """
        Get all valid diagonal moves for the bishop.

        :param board: The game board
        :return: List of valid positions to which the bishop can move
        """
        moves: List[Position] = []

        if self.position is None:
            return moves

        row, col = self.position

        # All 4 diagonal directions: up-left, up-right, down-left, down-right
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while board.is_within_bounds((r, c)):
                piece_at_dest = board.get_piece_at((r, c))
                if piece_at_dest is None:
                    moves.append((r, c))
                elif piece_at_dest.color != self.color:
                    moves.append((r, c))  # Can capture
                    break
                else:
                    break  # Friendly piece blocks path
                r += dr
                c += dc

        return moves