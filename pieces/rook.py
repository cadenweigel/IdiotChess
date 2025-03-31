from typing import List, TYPE_CHECKING
from .piece import Piece, Position

if TYPE_CHECKING:
    from app.board import Board  # Only for type hints

class Rook(Piece):
    """Represents a rook in a game of chess."""

    def get_valid_moves(self, board: 'Board') -> List[Position]:
        """
        Get all valid horizontal and vertical moves for the rook.
        """
        moves: List[Position] = []

        if self.position is None:
            return moves

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        row, col = self.position

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while board.is_within_bounds((r, c)):
                piece_at_dest = board.get_piece_at((r, c))
                if piece_at_dest is None:
                    moves.append((r, c))
                elif piece_at_dest.color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc

        return moves