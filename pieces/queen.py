from typing import List, TYPE_CHECKING
from .piece import Piece, Position

if TYPE_CHECKING:
    from app.board import Board  # Only for type hints


class Queen(Piece):
    """Represents a queen in a game of chess."""

    def get_valid_moves(self, board: 'Board') -> List[Position]:
        """
        Get all valid horizontal, vertical, and diagonal moves for the queen.

        :param board: The game board
        :return: List of valid positions to which the queen can move
        """
        moves: List[Position] = []

        if self.position is None:
            return moves

        row, col = self.position

        # 8 directions: rook + bishop directions
        directions = [
            (-1, 0), (1, 0),  # Vertical
            (0, -1), (0, 1),  # Horizontal
            (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonals
        ]

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
