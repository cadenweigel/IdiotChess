from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

from pieces import Pawn, Rook, Knight, Bishop, King, Queen

# Type alias for readability
Position = Tuple[int, int]

class Board:

    def __init__(self):
        # 8x8 board initialized with None
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.captured_pieces: List = []  # Store removed pieces

    def place_piece(self, piece, position):
        row, col = position
        self.grid[row][col] = piece
        piece.set_position(position)

    def remove_piece(self, position):
        """
        Remove a piece from the board and store it as captured.
        """
        row, col = position
        piece = self.grid[row][col]

        if piece:
            piece.set_position(None)  # Clear its position
            self.captured_pieces.append(piece)

        self.grid[row][col] = None

    def move_piece(self, from_pos: Position, to_pos: Position) -> bool:
        piece = self.get_piece_at(from_pos)
        if not piece or to_pos not in piece.get_valid_moves(self):
            return False  # Invalid move

        target = self.get_piece_at(to_pos)
        if target and target.color != piece.color:
            self.remove_piece(to_pos)  # Capture

        self.grid[to_pos[0]][to_pos[1]] = piece
        self.remove_piece(from_pos)
        piece.set_position(to_pos)
        piece.mark_as_moved()
        return True

    def get_piece_at(self, position):
        row, col = position
        return self.grid[row][col]

    def is_empty(self, position):
        return self.get_piece_at(position) is None

    def is_within_bounds(self, position):
        row, col = position
        return 0 <= row < 8 and 0 <= col < 8

    def get_captured_pieces(self) -> List:
        return self.captured_pieces

    def print_board(self):
        """
        Print the board using Unicode chess symbols.
        """
        unicode_pieces = {
            'white': {
                'Pawn': '♙',
                'Rook': '♖',
                'Knight': '♘',
                'Bishop': '♗',
                'Queen': '♕',
                'King': '♔',
            },
            'black': {
                'Pawn': '♟',
                'Rook': '♜',
                'Knight': '♞',
                'Bishop': '♝',
                'Queen': '♛',
                'King': '♚',
            }
        }

        for row in range(8):
            line = ""
            for col in range(8):
                piece = self.grid[row][col]
                if piece is None:
                    line += "· "  # middle dot for empty square
                else:
                    symbol = unicode_pieces[piece.color][piece.__class__.__name__]
                    line += f"{symbol} "
            print(f"{8 - row} {line}")
        print("  a b c d e f g h")

    def setup_standard_position(self):
        """Place all pieces in their standard chess starting positions."""

        # Set up white pieces (bottom of board)
        self.place_piece(Rook("white"), (7, 0))
        self.place_piece(Knight("white"), (7, 1))
        self.place_piece(Bishop("white"), (7, 2))
        self.place_piece(Queen("white"), (7, 3))
        self.place_piece(King("white"), (7, 4))
        self.place_piece(Bishop("white"), (7, 5))
        self.place_piece(Knight("white"), (7, 6))
        self.place_piece(Rook("white"), (7, 7))
        for col in range(8):
            self.place_piece(Pawn("white"), (6, col))

        # Set up black pieces (top of board)
        self.place_piece(Rook("black"), (0, 0))
        self.place_piece(Knight("black"), (0, 1))
        self.place_piece(Bishop("black"), (0, 2))
        self.place_piece(Queen("black"), (0, 3))
        self.place_piece(King("black"), (0, 4))
        self.place_piece(Bishop("black"), (0, 5))
        self.place_piece(Knight("black"), (0, 6))
        self.place_piece(Rook("black"), (0, 7))
        for col in range(8):
            self.place_piece(Pawn("black"), (1, col))

    