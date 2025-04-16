from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Tuple, Optional
import copy

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
        self.has_moved: bool = False  # Useful for castling, pawn logic

    def set_position(self, position: Position) -> None:
        """
        Set or update the current position of the piece.
        """
        self.position = position

    def mark_as_moved(self) -> None:
        """
        Mark the piece as having moved (used for castling, pawns, etc).
        """
        self.has_moved = True

    @abstractmethod
    def get_valid_moves(self, board: 'Board') -> List[Position]:
        """
        Return a list of valid moves for this piece.
        """
        pass

    @abstractmethod
    def symbol(self) -> str:
        """
        Return a string symbol representing this piece (e.g., 'N' for knight).
        """
        pass

    @abstractmethod
    def can_attack(self, target: Position, board: 'Board') -> bool:
        """
        Return whether this piece can attack the given target position.
        """
        pass

    def copy(self) -> Piece:
        """
        Return a deep copy of this piece (useful for move simulation).
        """
        return copy.deepcopy(self)

    def is_king(self) -> bool:
        return isinstance(self, King)

    def is_pawn(self) -> bool:
        return isinstance(self, Pawn)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.color}, {self.position})"







