from typing import List, TYPE_CHECKING
from .piece import Piece, Position
from utils.board_sim import simulate_move
import copy

if TYPE_CHECKING:
    from app.board import Board  # Only for type hints

class King(Piece):
    """Represents a king in a game of chess."""

    def get_valid_moves(self, board: 'Board', skip_check: bool = False) -> List[Position]:
        moves: List[Position] = []

        if self.position is None:
            return moves

        row, col = self.position

        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),          (0, 1),
            (1, -1),  (1, 0), (1, 1)
        ]

        for dr, dc in directions:
            new_pos = (row + dr, col + dc)
            if not board.is_within_bounds(new_pos):
                continue

            piece_at_dest = board.get_piece_at(new_pos)
            if piece_at_dest is None or piece_at_dest.color != self.color:
                if skip_check:
                    moves.append(new_pos)
                else:
                    sim = simulate_move(board, self.position, new_pos)
                    if not sim.is_in_check(self.color):
                        moves.append(new_pos)

        if not skip_check and not self.has_moved and not board.is_in_check(self.color):
            # Kingside
            kingside_rook = board.get_piece_at((row, 7))
            if (
                isinstance(kingside_rook, Piece) and kingside_rook.__class__.__name__ == 'Rook' and
                not kingside_rook.has_moved and
                board.is_empty((row, 5)) and board.is_empty((row, 6))
            ):
                if all(
                    not simulate_move(board, self.position, pos).is_in_check(self.color)
                    for pos in [(row, 5), (row, 6)]
                ):
                    moves.append((row, 6))

            # Queenside
            queenside_rook = board.get_piece_at((row, 0))
            if (
                isinstance(queenside_rook, Piece) and queenside_rook.__class__.__name__ == 'Rook' and
                not queenside_rook.has_moved and
                board.is_empty((row, 1)) and board.is_empty((row, 2)) and board.is_empty((row, 3))
            ):
                if all(
                    not simulate_move(board, self.position, pos).is_in_check(self.color)
                    for pos in [(row, 3), (row, 2)]
                ):
                    moves.append((row, 2))

        return moves


    def symbol(self) -> str:
        return 'K' if self.color == 'white' else 'k'

    def can_attack(self, target: Position, board: 'Board') -> bool:
        if self.position is None:
            return False

        row, col = self.position
        t_row, t_col = target

        return max(abs(row - t_row), abs(col - t_col)) == 1
