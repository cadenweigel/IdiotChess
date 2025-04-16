from app.board import Board
from pieces import King, Rook, Queen, Pawn


def test_king_movement_from_center():
    board = Board()
    king = King("white")
    board.place_piece(king, (4, 4))
    expected_moves = [
        (3, 3), (3, 4), (3, 5),
        (4, 3),         (4, 5),
        (5, 3), (5, 4), (5, 5)
    ]
    moves = king.get_valid_moves(board)
    assert set(moves) == set(expected_moves)


def test_kingside_castling():
    board = Board()
    king = King("white")
    rook = Rook("white")
    board.place_piece(king, (7, 4))
    board.place_piece(rook, (7, 7))

    assert board.get_piece_at((7, 5)) is None
    assert board.get_piece_at((7, 6)) is None

    moves = king.get_valid_moves(board)
    assert (7, 6) in moves


def test_queenside_castling():
    board = Board()
    king = King("white")
    rook = Rook("white")
    board.place_piece(king, (7, 4))
    board.place_piece(rook, (7, 0))

    for col in [1, 2, 3]:
        assert board.get_piece_at((7, col)) is None

    moves = king.get_valid_moves(board)
    assert (7, 2) in moves


def test_king_cannot_move_into_check():
    board = Board()
    king = King("white")
    enemy_rook = Rook("black")
    board.place_piece(king, (4, 4))
    board.place_piece(enemy_rook, (4, 7))

    moves = king.get_valid_moves(board)
    assert (4, 5) not in moves


def test_king_in_checkmate():
    board = Board()
    board.place_piece(King("white"), (7, 7))
    board.place_piece(Queen("black"), (6, 5))
    board.place_piece(Rook("black"), (5, 7))

    assert board.is_checkmate("white") is True


def test_king_in_check_but_not_mate():
    board = Board()
    board.place_piece(King("white"), (7, 7))
    board.place_piece(Queen("black"), (6, 6))  # now attacks diagonally

    assert board.is_in_check("white") is True
    assert board.is_checkmate("white") is False


def test_king_surrounded_by_friendly_pieces():
    board = Board()
    king = King("white")
    board.place_piece(king, (4, 4))
    for r, c in [
        (3, 3), (3, 4), (3, 5),
        (4, 3),         (4, 5),
        (5, 3), (5, 4), (5, 5)
    ]:
        board.place_piece(Pawn("white"), (r, c))

    moves = king.get_valid_moves(board)
    assert moves == []  # No legal squares


def test_king_can_escape_check_by_capture():
    board = Board()
    king = King("white")
    attacker = Queen("black")
    board.place_piece(king, (4, 4))
    board.place_piece(attacker, (3, 3))  # King can capture

    assert board.is_in_check("white")
    moves = king.get_valid_moves(board)
    assert (3, 3) in moves  # Capture to escape

def test_block_check_with_piece():
    board = Board()
    king = King("white")
    rook = Rook("black")
    blocker = Rook("white")

    board.place_piece(king, (7, 4))
    board.place_piece(rook, (0, 4))  # checking vertically

    # Check occurs only if nothing blocks
    assert board.is_in_check("white") is True

    # Now place blocker to stop the check
    board.place_piece(blocker, (5, 4))
    assert board.has_any_valid_moves("white") is True
    assert board.is_checkmate("white") is False


def test_capture_attacker_with_other_piece():
    board = Board()
    king = King("white")
    queen = Queen("black")
    defender = Rook("white")

    board.place_piece(king, (7, 7))
    board.place_piece(queen, (6, 6))     # attacks diagonally
    board.place_piece(defender, (5, 5))  # can capture the queen

    assert board.is_in_check("white") is True
    assert board.has_any_valid_moves("white") is True
    assert board.is_checkmate("white") is False

