from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Tuple, Optional

if TYPE_CHECKING:
    from .board import Board

# Type alias for readability
Position = Tuple[int, int]

class Piece(ABC):
    """Abstract base class for all chess pieces."""
    
    def __init__(self, color: str):
        """
        Initialize a piece with a color ('white' or 'black').
        """
        self.color: str = color
        self.position: Optional[Position] = None

    @abstractmethod
    def get_valid_moves(self, board: Board) -> List[Position]:
        """
        Abstract method to get all valid moves for the piece.
        returns list of valid positions the piece can move to
        """
        pass

    def set_position(self, position: Position) -> None:
        """
        Update the piece's position.
        """
        self.position = position

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.color})"


class Pawn(Piece):

    def get_valid_moves(self, board: Board) -> List[Position]:
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

class Rook(Piece):
    """Represents a rook in a game of chess."""

    def get_valid_moves(self, board: Board) -> List[Position]:
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

class Knight(Piece):
    """Represents a knight in a game of chess."""

    def get_valid_moves(self, board: Board) -> List[Position]:
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

class Bishop(Piece):
    """Represents a bishop in a game of chess."""

    def get_valid_moves(self, board: Board) -> List[Position]:
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

class Queen(Piece):
    """Represents a queen in a game of chess."""

    def get_valid_moves(self, board: Board) -> List[Position]:
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

class King(Piece):
    """Represents a king in a game of chess."""

    def get_valid_moves(self, board: Board) -> List[Position]:
        """
        Get all valid one-square moves in any direction for the king.

        :param board: The game board
        :return: List of valid positions to which the king can move
        """
        moves: List[Position] = []

        if self.position is None:
            return moves

        row, col = self.position

        # All 8 surrounding squares
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
                moves.append(new_pos)

        return moves
