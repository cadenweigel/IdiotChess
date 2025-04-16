import pytest
from app.board import Board
from pieces import Queen, King, Rook, Pawn


@pytest.mark.parametrize("color, position, expected_count", [
    ("white", (4, 4), 27),
    ("black", (0, 0), 21),
])
def test_queen_movement_range(color, position, expected_count):
    board = Board()
    queen = Queen(color)
    board.place_piece(queen, position)

    moves = queen.get_valid_moves(board)
    assert len(moves) == expected_count


@pytest.mark.parametrize("queen_pos, blocker_pos, direction_blocked", [
    ((4, 4), (4, 6), [(4, 6), (4, 7)]),
    ((4, 4), (2, 2), [(2, 2), (1, 1), (0, 0)]),
])
def test_queen_blocked_by_friendly_piece(queen_pos, blocker_pos, direction_blocked):
    board = Board()
    queen = Queen("white")
    blocker = Pawn("white")
    board.place_piece(queen, queen_pos)
    board.place_piece(blocker, blocker_pos)

    moves = queen.get_valid_moves(board)
    for pos in direction_blocked:
        assert pos not in moves


@pytest.mark.parametrize("queen_pos, enemy_pos, can_reach", [
    ((4, 4), (4, 6), True),
    ((4, 4), (2, 2), True),
    ((4, 4), (6, 5), False),
])
def test_queen_can_capture_enemy_piece(queen_pos, enemy_pos, can_reach):
    board = Board()
    queen = Queen("white")
    enemy = Pawn("black")
    board.place_piece(queen, queen_pos)
    board.place_piece(enemy, enemy_pos)

    moves = queen.get_valid_moves(board)
    if can_reach:
        assert enemy_pos in moves
    else:
        assert enemy_pos not in moves


@pytest.mark.parametrize("queen_pos, target_pos, expect_attack", [
    ((4, 4), (4, 7), True),
    ((4, 4), (7, 4), True),
    ((4, 4), (7, 7), True),
    ((4, 4), (5, 6), False),
])
def test_queen_can_attack(queen_pos, target_pos, expect_attack):
    board = Board()
    queen = Queen("white")
    board.place_piece(queen, queen_pos)

    result = queen.can_attack(target_pos, board)
    assert result is expect_attack


@pytest.mark.parametrize("king_color, king_pos, queen_color, queen_pos, helper_pieces, expected_check, expected_mate", [
    ("white", (7, 7), "black", (7, 0), [], True, False),
    ("black", (0, 0), "white", (0, 7), [], True, False),

    ("white", (7, 7), "black", (6, 5), [("black", Rook, (5, 7))], True, True),
    ("black", (0, 0), "white", (1, 2), [("white", Rook, (2, 0))], True, True),

    # FIXED ↓↓↓ These queens are blocked, so not check
    ("white", (7, 7), "black", (4, 7), [("white", Rook, (6, 7))], False, False),
    ("black", (0, 0), "white", (3, 0), [("black", Rook, (1, 0))], False, False),

    ("white", (7, 7), "black", (6, 6), [("white", Rook, (5, 5))], True, False),
    ("black", (0, 0), "white", (1, 1), [("black", Rook, (2, 2))], True, False),
])
def test_queen_check_scenarios(king_color, king_pos, queen_color, queen_pos, helper_pieces, expected_check, expected_mate):
    board = Board()
    board.place_piece(King(king_color), king_pos)
    board.place_piece(Queen(queen_color), queen_pos)

    for color, piece_cls, pos in helper_pieces:
        board.place_piece(piece_cls(color), pos)

    assert board.is_in_check(king_color) is expected_check
    assert board.is_checkmate(king_color) is expected_mate
    assert board.has_any_valid_moves(king_color) is not expected_mate
