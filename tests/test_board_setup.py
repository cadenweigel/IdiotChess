import unittest
from app.board import Board
from pieces import Pawn, Rook, Knight, Bishop, King, Queen


class TestBoardSetup(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.board.setup_standard_position()

    def test_total_piece_count(self):
        """Ensure there are 32 total pieces on the board."""
        count = sum(
            1 for row in self.board.grid for piece in row if piece is not None
        )
        self.assertEqual(count, 32)

    def test_pawn_positions(self):
        """Check all pawns are in correct starting positions."""
        for col in range(8):
            white_pawn = self.board.get_piece_at((6, col))
            black_pawn = self.board.get_piece_at((1, col))
            self.assertIsInstance(white_pawn, Pawn)
            self.assertEqual(white_pawn.color, "white")
            self.assertIsInstance(black_pawn, Pawn)
            self.assertEqual(black_pawn.color, "black")

    def test_major_piece_positions(self):
        """Check that the major pieces are in the right places."""
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        for col, piece_type in enumerate(piece_order):
            white_piece = self.board.get_piece_at((7, col))
            black_piece = self.board.get_piece_at((0, col))

            self.assertIsInstance(white_piece, piece_type)
            self.assertEqual(white_piece.color, "white")

            self.assertIsInstance(black_piece, piece_type)
            self.assertEqual(black_piece.color, "black")


if __name__ == "__main__":
    unittest.main()
