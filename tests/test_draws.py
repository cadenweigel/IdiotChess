import pytest
from app.board import Board
from pieces import King, Queen, Rook, Knight, Bishop, Pawn


def test_draw_by_stalemate():
    board = Board()
    board.place_piece(King("white"), (7, 7))
    board.place_piece(Queen("black"), (6, 5))
    board.place_piece(King("black"), (5, 5))
    assert board.is_draw("white") is True


def test_draw_by_insufficient_material():
    board = Board()
    board.place_piece(King("white"), (7, 7))
    board.place_piece(Knight("white"), (6, 5))
    board.place_piece(King("black"), (0, 0))
    assert board.is_draw("white") is True


def test_draw_by_fifty_move_rule():
    board = Board()
    board.place_piece(King("white"), (7, 7))
    board.place_piece(King("black"), (0, 0))
    board.halfmove_clock = 100
    assert board.is_draw("white") is True


def test_draw_by_threefold_repetition():
    board = Board()
    board.place_piece(King("white"), (7, 7))
    board.place_piece(King("black"), (0, 0))
    board.place_piece(Knight("white"), (6, 5))

    for _ in range(3):
        board.move_piece((6, 5), (5, 3))
        board.move_piece((0, 0), (0, 0))
        board.move_piece((5, 3), (6, 5))
        board.move_piece((0, 0), (0, 0))

    assert board.is_draw("white") is True


def test_not_draw_if_conditions_not_met():
    board = Board()
    board.place_piece(King("white"), (7, 7))
    board.place_piece(King("black"), (0, 0))
    board.place_piece(Pawn("white"), (6, 0))
    board.halfmove_clock = 3
    assert board.is_draw("white") is False
