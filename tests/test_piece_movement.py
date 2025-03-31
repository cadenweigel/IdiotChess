import unittest
from app.board import Board
from app.pieces import Pawn, Rook, Knight, Bishop, Queen, King


class TestPieceMovement(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_white_pawn_initial_moves(self):
        pawn = Pawn("white")
        self.board.place_piece(pawn, (6, 4))  # e2
        moves = pawn.get_valid_moves(self.board)
        self.assertIn((5, 4), moves)  # one step forward
        self.assertIn((4, 4), moves)  # two steps forward
        self.assertEqual(len(moves), 2)

    def test_black_pawn_initial_moves(self):
        pawn = Pawn("black")
        self.board.place_piece(pawn, (1, 4))  # e7
        moves = pawn.get_valid_moves(self.board)
        self.assertIn((2, 4), moves)
        self.assertIn((3, 4), moves)
        self.assertEqual(len(moves), 2)

    def test_rook_movement(self):
        rook = Rook("white")
        self.board.place_piece(rook, (4, 4))
        moves = rook.get_valid_moves(self.board)
        expected_directions = [
            (0, 4), (1, 4), (2, 4), (3, 4),
            (5, 4), (6, 4), (7, 4),  # vertical
            (4, 0), (4, 1), (4, 2), (4, 3),
            (4, 5), (4, 6), (4, 7)   # horizontal
        ]
        for move in expected_directions:
            self.assertIn(move, moves)
        self.assertEqual(len(moves), 14)

    def test_knight_movement(self):
        knight = Knight("white")
        self.board.place_piece(knight, (4, 4))
        expected_moves = [
            (2, 3), (2, 5),
            (3, 2), (3, 6),
            (5, 2), (5, 6),
            (6, 3), (6, 5)
        ]
        moves = knight.get_valid_moves(self.board)
        self.assertEqual(set(moves), set(expected_moves))

    def test_bishop_movement(self):
        bishop = Bishop("white")
        self.board.place_piece(bishop, (3, 3))
        moves = bishop.get_valid_moves(self.board)
        expected_moves = [
            (2, 2), (1, 1), (0, 0),
            (2, 4), (1, 5), (0, 6),
            (4, 2), (5, 1), (6, 0),
            (4, 4), (5, 5), (6, 6), (7, 7)
        ]
        self.assertEqual(set(moves), set(expected_moves))

    def test_queen_movement(self):
        queen = Queen("white")
        self.board.place_piece(queen, (4, 4))
        moves = queen.get_valid_moves(self.board)
        # Rook + bishop moves = 27 possible destinations
        self.assertEqual(len(moves), 27)

    def test_king_movement(self):
        king = King("white")
        self.board.place_piece(king, (4, 4))
        expected_moves = [
            (3, 3), (3, 4), (3, 5),
            (4, 3),         (4, 5),
            (5, 3), (5, 4), (5, 5)
        ]
        moves = king.get_valid_moves(self.board)
        self.assertEqual(set(moves), set(expected_moves))


if __name__ == "__main__":
    unittest.main()
