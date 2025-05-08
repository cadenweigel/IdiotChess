from typing import List, TYPE_CHECKING
from .piece import Piece, Position

if TYPE_CHECKING:
    from app.board import Board  # Only for type hints


class Pawn(Piece):
    def get_valid_moves(self, board: 'Board') -> List[Position]:
        """
        Return a list of valid moves for the pawn, including:
        - one step forward
        - two steps forward from starting row
        - diagonal captures
        """
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

        # En passant
        if hasattr(board, "last_move") and board.last_move:
            last_from, last_to = board.last_move
            last_piece = board.get_piece_at(last_to)
            if (
                isinstance(last_piece, Pawn) and
                last_piece.color != self.color and
                abs(last_from[0] - last_to[0]) == 2 and  # moved two squares
                last_to[0] == row and  # same row as our pawn
                abs(last_to[1] - col) == 1  # adjacent column
            ):
                en_passant_target = (row + direction, last_to[1])
                if board.is_within_bounds(en_passant_target):
                    moves.append(en_passant_target)

        return moves

    def symbol(self) -> str:
        """Return the symbol representing this pawn."""
        return 'P' if self.color == 'white' else 'p'

    def can_attack(self, target: Position, board: 'Board') -> bool:
        """
        Return True if this pawn can attack the given target square diagonally.
        """
        if self.position is None:
            return False

        row, col = self.position
        direction = -1 if self.color == 'white' else 1
        target_row, target_col = target

        piece = board.get_piece_at(target)
        return (
            abs(target_col - col) == 1 and
            (target_row - row) == direction and
            piece is not None and
            piece.color != self.color
        )
