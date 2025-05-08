import pytest
from app.board import Board
from pieces import Knight, King, Rook, Pawn


@pytest.mark.parametrize("color, position, expected_moves", [
    ("white", (4, 4), {(2, 3), (2, 5), (3, 2), (3, 6), (5, 2), (5, 6), (6, 3), (6, 5)}),
    ("black", (0, 0), {(1, 2), (2, 1)}),
])
def test_knight_movement_range(color, position, expected_moves):
    board = Board()
    knight = Knight(color)
    board.place_piece(knight, position)

    moves = set(knight.get_valid_moves(board))
    assert moves == expected_moves


@pytest.mark.parametrize("knight_pos, blocker_positions", [
    ((4, 4), [(2, 3), (6, 3), (3, 6)]),  # Friendly pawns block these moves
])
def test_knight_blocked_by_friendly(knight_pos, blocker_positions):
    board = Board()
    knight = Knight("white")
    board.place_piece(knight, knight_pos)

    for pos in blocker_positions:
        board.place_piece(Pawn("white"), pos)

    moves = knight.get_valid_moves(board)
    for pos in blocker_positions:
        assert pos not in moves


@pytest.mark.parametrize("knight_pos, enemy_pos", [
    ((4, 4), (2, 3)),
    ((4, 4), (6, 5)),
])
def test_knight_can_capture_enemy(knight_pos, enemy_pos):
    board = Board()
    knight = Knight("white")
    board.place_piece(knight, knight_pos)
    board.place_piece(Pawn("black"), enemy_pos)

    moves = knight.get_valid_moves(board)
    assert enemy_pos in moves


@pytest.mark.parametrize("knight_pos, target_pos, expect_attack", [
    ((4, 4), (2, 3), True),
    ((4, 4), (6, 5), True),
    ((4, 4), (4, 5), False),
])
def test_knight_can_attack(knight_pos, target_pos, expect_attack):
    board = Board()
    knight = Knight("black")
    board.place_piece(knight, knight_pos)

    result = knight.can_attack(target_pos, board)
    assert result is expect_attack


@pytest.mark.parametrize("king_color, king_pos, knight_color, knight_pos, helper_pieces, expected_check, expected_mate", [
    # Simple knight check
    ("white", (4, 4), "black", (2, 3), [], True, False),
    ("black", (3, 3), "white", (5, 4), [], True, False),

    # Knight delivers checkmate with Rook covering diagonals (FIXED)
    ("white", (7, 7), "black", (5, 6), [("black", Rook, (6, 7)), ("black", Rook, (6, 6))], True, True),
    ("black", (0, 0), "white", (2, 1), [("white", Rook, (1, 0)), ("white", Rook, (1, 1))], True, True),

    # Knight check that can be captured
    ("white", (7, 7), "black", (5, 6), [("white", Rook, (5, 6))], False, False),
    ("black", (0, 0), "white", (2, 1), [("black", Rook, (2, 1))], False, False),
])

def test_knight_check_scenarios(king_color, king_pos, knight_color, knight_pos, helper_pieces, expected_check, expected_mate):
    board = Board()
    board.place_piece(King(king_color), king_pos)
    board.place_piece(Knight(knight_color), knight_pos)

    for color, piece_cls, pos in helper_pieces:
        board.place_piece(piece_cls(color), pos)

    assert board.is_in_check(king_color) is expected_check
    assert board.is_checkmate(king_color) is expected_mate
    assert board.has_any_valid_moves(king_color) is not expected_mate
