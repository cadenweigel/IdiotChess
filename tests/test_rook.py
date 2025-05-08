import pytest
from app.board import Board
from pieces import Rook, King, Pawn


@pytest.mark.parametrize("color, position, expected_count", [
    ("white", (4, 4), 14),
    ("black", (0, 0), 14),
])
def test_rook_movement_range(color, position, expected_count):
    board = Board()
    rook = Rook(color)
    board.place_piece(rook, position)

    moves = rook.get_valid_moves(board)
    assert len(moves) == expected_count
    assert position not in moves


@pytest.mark.parametrize("rook_pos, blocker_pos, blocked_moves", [
    ((4, 4), (4, 6), [(4, 6), (4, 7)]),
    ((4, 4), (1, 4), [(0, 4), (1, 4)]),
])
def test_rook_blocked_by_friendly_piece(rook_pos, blocker_pos, blocked_moves):
    board = Board()
    rook = Rook("white")
    blocker = Pawn("white")
    board.place_piece(rook, rook_pos)
    board.place_piece(blocker, blocker_pos)

    moves = rook.get_valid_moves(board)
    for pos in blocked_moves:
        assert pos not in moves


@pytest.mark.parametrize("rook_pos, enemy_pos, can_reach", [
    ((4, 4), (4, 6), True),
    ((4, 4), (2, 4), True),
    ((4, 4), (3, 3), False),
])
def test_rook_can_capture_enemy_piece(rook_pos, enemy_pos, can_reach):
    board = Board()
    rook = Rook("white")
    enemy = Pawn("black")
    board.place_piece(rook, rook_pos)
    board.place_piece(enemy, enemy_pos)

    moves = rook.get_valid_moves(board)
    if can_reach:
        assert enemy_pos in moves
    else:
        assert enemy_pos not in moves


@pytest.mark.parametrize("rook_pos, target_pos, expect_attack", [
    ((4, 4), (4, 7), True),
    ((4, 4), (0, 4), True),
    ((4, 4), (4, 4), False),
    ((4, 4), (3, 3), False),
])
def test_rook_can_attack(rook_pos, target_pos, expect_attack):
    board = Board()
    rook = Rook("black")
    board.place_piece(rook, rook_pos)

    result = rook.can_attack(target_pos, board)
    assert result is expect_attack


@pytest.mark.parametrize("king_color, king_pos, rook_color, rook_pos, helper_pieces, expected_check, expected_mate", [
    # Simple check from a rook
    ("white", (7, 7), "black", (7, 0), [], True, False),
    ("black", (0, 0), "white", (0, 7), [], True, False),

    # Rook + rook checkmate (fixed with additional diagonal cover)
    ("white", (7, 7), "black", (7, 0), [("black", Rook, (6, 7)), ("black", Rook, (6, 6))], True, True),
    ("black", (0, 0), "white", (0, 7), [("white", Rook, (1, 0)), ("white", Rook, (1, 1))], True, True),

    # Rook check that can be blocked
    ("white", (7, 7), "black", (4, 7), [("white", Pawn, (6, 7))], False, False),
    ("black", (0, 0), "white", (3, 0), [("black", Pawn, (1, 0))], False, False),

    # Rook check that can be captured
    ("white", (7, 7), "black", (6, 7), [("white", Rook, (5, 7))], True, False),
    ("black", (0, 0), "white", (1, 0), [("black", Rook, (2, 0))], True, False),
])
def test_rook_check_scenarios(king_color, king_pos, rook_color, rook_pos, helper_pieces, expected_check, expected_mate):
    board = Board()
    board.place_piece(King(king_color), king_pos)
    board.place_piece(Rook(rook_color), rook_pos)

    for color, piece_cls, pos in helper_pieces:
        board.place_piece(piece_cls(color), pos)

    assert board.is_in_check(king_color) is expected_check
    assert board.is_checkmate(king_color) is expected_mate
    assert board.has_any_valid_moves(king_color) is not expected_mate
