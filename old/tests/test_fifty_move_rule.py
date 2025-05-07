import pytest
from app.board import Board
from pieces import King, Rook, Pawn


def test_fifty_move_rule_not_triggered_early():
    board = Board()
    board.place_piece(King("white"), (7, 7))
    board.place_piece(King("black"), (0, 0))
    board.halfmove_clock = 99

    # One more move still doesn't trigger
    assert board.is_fifty_move_rule() is False
    board.halfmove_clock += 1
    assert board.is_fifty_move_rule() is True


def test_fifty_move_rule_resets_on_pawn_move():
    board = Board()
    board.place_piece(King("white"), (7, 7))
    board.place_piece(King("black"), (0, 0))
    board.place_piece(Pawn("white"), (6, 0))
    board.halfmove_clock = 99

    board.move_piece((6, 0), (5, 0))  # Pawn move should reset counter
    assert board.halfmove_clock == 0
    assert board.is_fifty_move_rule() is False


def test_fifty_move_rule_resets_on_capture():
    board = Board()
    board.place_piece(King("white"), (7, 7))
    board.place_piece(King("black"), (0, 0))
    board.place_piece(Rook("white"), (5, 5))
    board.place_piece(Rook("black"), (4, 5))
    board.halfmove_clock = 99

    board.move_piece((5, 5), (4, 5))  # Capture resets counter
    assert board.halfmove_clock == 0
    assert board.is_fifty_move_rule() is False
