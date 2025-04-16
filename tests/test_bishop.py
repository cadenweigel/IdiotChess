import pytest
from app.board import Board
from pieces import Bishop, King, Rook, Pawn


@pytest.mark.parametrize("color, position, expected_count", [
    ("white", (4, 4), 13),
    ("black", (0, 0), 7),
])
def test_bishop_movement_range(color, position, expected_count):
    board = Board()
    bishop = Bishop(color)
    board.place_piece(bishop, position)

    moves = bishop.get_valid_moves(board)
    assert len(moves) == expected_count


@pytest.mark.parametrize("bishop_pos, blockers", [
    ((4, 4), [(2, 2), (5, 5)]),  # Top-left and bottom-right
])
def test_bishop_blocked_by_friendly_piece(bishop_pos, blockers):
    board = Board()
    bishop = Bishop("white")
    board.place_piece(bishop, bishop_pos)

    for pos in blockers:
        board.place_piece(Pawn("white"), pos)

    moves = bishop.get_valid_moves(board)
    for pos in blockers:
        assert pos not in moves


@pytest.mark.parametrize("bishop_pos, enemy_pos, can_reach", [
    ((4, 4), (2, 2), True),
    ((4, 4), (6, 6), True),
    ((4, 4), (4, 6), False),
])
def test_bishop_can_capture_enemy(bishop_pos, enemy_pos, can_reach):
    board = Board()
    bishop = Bishop("white")
    enemy = Pawn("black")
    board.place_piece(bishop, bishop_pos)
    board.place_piece(enemy, enemy_pos)

    moves = bishop.get_valid_moves(board)
    assert (enemy_pos in moves) == can_reach


@pytest.mark.parametrize("bishop_pos, target_pos, expect_attack", [
    ((4, 4), (2, 2), True),
    ((4, 4), (6, 6), True),
    ((4, 4), (5, 3), True),
    ((4, 4), (4, 4), False),
    ((4, 4), (4, 6), False),
])
def test_bishop_can_attack(bishop_pos, target_pos, expect_attack):
    board = Board()
    bishop = Bishop("black")
    board.place_piece(bishop, bishop_pos)

    result = bishop.can_attack(target_pos, board)
    assert result is expect_attack


@pytest.mark.parametrize("king_color, king_pos, bishop_color, bishop_pos, helper_pieces, expected_check, expected_mate", [
    # Simple check
    ("white", (4, 4), "black", (1, 1), [], True, False),
    ("black", (3, 3), "white", (6, 6), [], True, False),

    # Bishop delivers checkmate with diagonal + rook covering escape (FIXED)
    ("white", (7, 7), "black", (5, 5), [("black", Rook, (6, 6)), ("black", Rook, (6, 7))], True, True),
    ("black", (0, 0), "white", (2, 2), [("white", Rook, (1, 1)), ("white", Rook, (1, 0))], True, True),

    # Bishop check that can be captured
    ("white", (7, 7), "black", (5, 5), [("white", Rook, (5, 5))], False, False),
    ("black", (0, 0), "white", (2, 2), [("black", Rook, (2, 2))], False, False),
])
def test_bishop_check_scenarios(king_color, king_pos, bishop_color, bishop_pos, helper_pieces, expected_check, expected_mate):
    board = Board()
    board.place_piece(King(king_color), king_pos)
    board.place_piece(Bishop(bishop_color), bishop_pos)

    for color, piece_cls, pos in helper_pieces:
        board.place_piece(piece_cls(color), pos)

    assert board.is_in_check(king_color) is expected_check
    assert board.is_checkmate(king_color) is expected_mate
    assert board.has_any_valid_moves(king_color) is not expected_mate
