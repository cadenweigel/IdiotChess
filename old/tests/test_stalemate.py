import pytest
from app.board import Board
from pieces import King, Queen, Rook, Pawn


@pytest.mark.parametrize("king_color, king_pos, opponents, expected_stalemate", [
    # ✅ Classic white king stalemate (not in check, no legal moves)
    ("white", (7, 7), [
        ("black", Queen, (6, 5)),
        ("black", King, (5, 5)),
    ], True),

    # ✅ Classic black king stalemate (mirrored)
    ("black", (0, 0), [
        ("white", Queen, (1, 2)),
        ("white", King, (2, 2)),
    ], True),

    # ✅ White king trapped by black pawns (not in check)
    ("white", (7, 7), [
        ("black", Pawn, (6, 6)),
        ("black", Pawn, (6, 7)),
        ("black", King, (5, 5)),
    ], True),

    # ❌ Not stalemate – white king has at least one move
    ("white", (7, 7), [
        ("black", Queen, (5, 5)),  # Not close enough to restrict king fully
        ("black", King, (5, 3)),
    ], False),

    # ❌ Not stalemate – black king has multiple escape options
    ("black", (0, 0), [
        ("white", Rook, (0, 7)),
        ("white", Rook, (7, 0)),
        ("white", King, (7, 7)),
    ], False),
])
def test_stalemate_scenarios(king_color, king_pos, opponents, expected_stalemate):
    board = Board()
    board.place_piece(King(king_color), king_pos)

    for color, piece_cls, pos in opponents:
        board.place_piece(piece_cls(color), pos)

    assert board
