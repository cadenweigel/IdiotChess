import pytest
from app.board import Board
from pieces import King, Queen, Rook, Bishop, Knight


@pytest.mark.parametrize("king_color, king_pos, attackers, expected_checkmate", [
    # Queen + rook mate
    ("white", (7, 7), [
        ("black", Queen, (6, 5)),
        ("black", Rook, (5, 7)),
    ], True),

    ("black", (0, 0), [
        ("white", Queen, (1, 2)),
        ("white", Rook, (2, 0)),
    ], True),

    # Rook + rook ladder mate (now sealed with diagonal rook)
    ("white", (7, 7), [
        ("black", Rook, (7, 5)),
        ("black", Rook, (6, 7)),
        ("black", Rook, (6, 6)),
    ], True),

    ("black", (0, 0), [
        ("white", Rook, (0, 2)),
        ("white", Rook, (1, 0)),
        ("white", Rook, (1, 1)),
    ], True),

    # Bishop + knight + rook combo (fixed with extra rook to seal)
    ("white", (7, 7), [
        ("black", Bishop, (6, 5)),
        ("black", Knight, (5, 6)),
        ("black", Rook, (6, 6)),
        ("black", Rook, (6, 7)),
    ], True),

    # Check but not mate
    ("white", (7, 7), [
        ("black", Queen, (5, 5)),
    ], False),

    ("black", (0, 0), [
        ("white", Rook, (0, 2)),
    ], False),
])
def test_checkmate_patterns(king_color, king_pos, attackers, expected_checkmate):
    board = Board()
    board.place_piece(King(king_color), king_pos)

    for color, piece_cls, pos in attackers:
        board.place_piece(piece_cls(color), pos)

    assert board.is_in_check(king_color) is True
    assert board.is_checkmate(king_color) is expected_checkmate
    assert board.has_any_valid_moves(king_color) is not expected_checkmate
