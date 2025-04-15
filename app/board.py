from __future__ import annotations
from typing import Optional, List, Tuple
from pieces import Pawn, Rook, Knight, Bishop, King, Queen
import copy

# Type alias for readability
Position = Tuple[int, int]

class Board:

    def __init__(self):
        # 8x8 board initialized with None
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.captured_pieces: List = []  # Store removed pieces
        self.last_move: Optional[Tuple[Position, Position]] = None  # Track last move (for en passant)

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
            piece.set_position(None)
            self.captured_pieces.append(piece)

        self.grid[row][col] = None

    def move_piece(self, from_pos: Position, to_pos: Position, promotion_piece_cls=None, validate: bool = True) -> bool:
        """
        Move a piece from one position to another.
        Supports capturing, en passant, pawn promotion, and castling.
        If validate=False, skips checking if the move is in the piece's legal move list.
        """
        piece = self.get_piece_at(from_pos)
        if validate and (not piece or to_pos not in piece.get_valid_moves(self)):
            return False  # Invalid move

        # Handle castling
        if isinstance(piece, King) and abs(from_pos[1] - to_pos[1]) == 2:
            self.handle_castling(piece, from_pos, to_pos)

        # Handle en passant
        if isinstance(piece, Pawn) and self.is_en_passant_capture(piece, from_pos, to_pos):
            self.handle_en_passant(piece, from_pos, to_pos)
        else:
            self.handle_capture(to_pos)

        self.grid[to_pos[0]][to_pos[1]] = piece
        self.remove_piece(from_pos)
        piece.set_position(to_pos)
        piece.mark_as_moved()
        self.last_move = (from_pos, to_pos)

        if isinstance(piece, Pawn):
            self.handle_promotion(piece, to_pos, promotion_piece_cls)

        return True

    def handle_castling(self, king: King, from_pos: Position, to_pos: Position):
        row = from_pos[0]
        if to_pos[1] == 6:
            # Kingside castling
            rook_from, rook_to = (row, 7), (row, 5)
        elif to_pos[1] == 2:
            # Queenside castling
            rook_from, rook_to = (row, 0), (row, 3)
        else:
            return  # Not a castling move

        rook = self.get_piece_at(rook_from)
        self.grid[rook_to[0]][rook_to[1]] = rook
        self.grid[rook_from[0]][rook_from[1]] = None
        rook.set_position(rook_to)
        rook.mark_as_moved()

    def is_in_check(self, color: str) -> bool:
        king_pos = None

        # Find the king's position
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.color == color and piece.__class__.__name__ == 'King':
                    king_pos = (row, col)
                    break
            if king_pos:
                break

        if not king_pos:
            return False  # King not found (shouldn't happen in normal play)

        # Check if any enemy piece can attack the king
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.color != color:
                    if piece.can_attack(king_pos, self):
                        return True

        return False

    def has_any_valid_moves(self, color: str) -> bool:
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.color == color:
                    for move in piece.get_valid_moves(self):
                        test_board = copy.deepcopy(self)
                        if test_board.move_piece(piece.position, move) and not test_board.is_in_check(color):
                            return True
        return False

    def is_checkmate(self, color: str) -> bool:
        return self.is_in_check(color) and not self.has_any_valid_moves(color)

    def is_stalemate(self, color: str) -> bool:
        return not self.is_in_check(color) and not self.has_any_valid_moves(color)

    def is_en_passant_capture(self, pawn: Pawn, from_pos: Position, to_pos: Position) -> bool:
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        if abs(from_col - to_col) != 1 or not self.is_empty(to_pos):
            return False

        if not self.last_move:
            return False

        last_from, last_to = self.last_move
        last_piece = self.get_piece_at(last_to)

        return (
            isinstance(last_piece, Pawn) and
            last_piece.color != pawn.color and
            abs(last_from[0] - last_to[0]) == 2 and
            last_to[0] == from_row and
            last_to[1] == to_col
        )

    def handle_en_passant(self, pawn: Pawn, from_pos: Position, to_pos: Position):
        captured_row = from_pos[0]
        captured_col = to_pos[1]
        self.remove_piece((captured_row, captured_col))

    def handle_capture(self, to_pos: Position):
        target = self.get_piece_at(to_pos)
        if target and target.color != self.get_piece_at(to_pos).color:
            self.remove_piece(to_pos)

    def handle_promotion(self, pawn: Pawn, to_pos: Position, promotion_piece_cls=None):
        final_row = 0 if pawn.color == 'white' else 7
        if to_pos[0] == final_row:
            from pieces import Queen  # Avoid circular import
            promoted_cls = promotion_piece_cls or Queen
            promoted_piece = promoted_cls(pawn.color)
            self.place_piece(promoted_piece, to_pos)

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
                    line += "· "
                else:
                    symbol = unicode_pieces[piece.color][piece.__class__.__name__]
                    line += f"{symbol} "
            print(f"{8 - row} {line}")
        print("  a b c d e f g h")

    def setup_standard_position(self):
        """Place all pieces in their standard chess starting positions."""
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
