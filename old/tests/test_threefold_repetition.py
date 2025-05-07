import pytest
from app.board import Board
from pieces import King, Knight


def test_threefold_repetition_trigger():
    board = Board()
    board.place_piece(King("white"), (7, 7))
    board.place_piece(King("black"), (0, 0))
    board.place_piece(Knight("white"), (6, 5))

    # Simulate moving the knight back and forth
    for _ in range(3):
        board.move_piece((6, 5), (5, 3))  # White
        board.move_piece((0, 0), (0, 0))  # Black (pass)
        board.move_piece((5, 3), (6, 5))  # White
        board.move_piece((0, 0), (0, 0))  # Black (pass)

    assert board.is_threefold_repetition() is True


def test_twofold_repetition_is_not_draw():
    board = Board()
    board.place_piece(King("white"), (7, 7))
    board.place_piece(King("black"), (0, 0))
    board.place_piece(Knight("white"), (6, 5))

    # Only two repetitions
    for _ in range(2):
        board.move_piece((6, 5), (5, 3))
        board.move_piece((0, 0), (0, 0))
        board.move_piece((5, 3), (6, 5))
        board.move_piece((0, 0), (0, 0))

    assert board.is_threefold_repetition() is False
