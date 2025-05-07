import pytest
from app.board import Board
from pieces import King, Queen, Rook, Bishop, Knight


@pytest.mark.parametrize("pieces, expected_draw", [
    # ✅ Bare kings
    ([
        ("white", King, (7, 7)),
        ("black", King, (0, 0)),
    ], True),

    # ✅ King and bishop vs king
    ([
        ("white", King, (7, 7)),
        ("white", Bishop, (5, 5)),
        ("black", King, (0, 0)),
    ], True),

    # ✅ King and knight vs king
    ([
        ("white", King, (7, 7)),
        ("white", Knight, (5, 5)),
        ("black", King, (0, 0)),
    ], True),

    # 🔴 King and queen vs king (can checkmate)
    ([
        ("white", King, (7, 7)),
        ("white", Queen, (5, 5)),
        ("black", King, (0, 0)),
    ], False),

    # 🔴 King and rook vs king
    ([
        ("white", King, (7, 7)),
        ("white", Rook, (6, 0)),
        ("black", King, (0, 0)),
    ], False),

    # 🔴 King and bishop + bishop vs king (if on opposite colors, can mate)
    ([
        ("white", King, (7, 7)),
        ("white", Bishop, (5, 5)),  # dark square
        ("white", Bishop, (3, 4)),  # light square
        ("black", King, (0, 0)),
    ], False),
])
def test_insufficient_material(pieces, expected_draw):
    board = Board()

    for color, piece_cls, pos in pieces:
        board.place_piece(piece_cls(color), pos)

    assert board.is_insufficient_material() is expected_draw
