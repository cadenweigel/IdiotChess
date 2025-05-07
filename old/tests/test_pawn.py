import pytest
from app.board import Board
from pieces import Pawn


@pytest.mark.parametrize("color, start_row, one_step, two_step", [
    ("white", 6, (5, 4), (4, 4)),  # e2 to e3/e4
    ("black", 1, (2, 4), (3, 4)),  # e7 to e6/e5
])
def test_pawn_single_and_double_move(color, start_row, one_step, two_step):
    board = Board()
    pawn = Pawn(color)
    board.place_piece(pawn, (start_row, 4))
    moves = pawn.get_valid_moves(board)
    assert one_step in moves
    assert two_step in moves


def test_pawn_blocked_move():
    board = Board()
    pawn = Pawn("white")
    blocker = Pawn("white")
    board.place_piece(pawn, (6, 4))
    board.place_piece(blocker, (5, 4))
    moves = pawn.get_valid_moves(board)
    assert (5, 4) not in moves
    assert (4, 4) not in moves


@pytest.mark.parametrize("color, attacker_pos, enemy_pos, expected_capture_pos", [
    ("white", (4, 4), (3, 3), (3, 3)),
    ("black", (3, 3), (4, 4), (4, 4)),
])
def test_pawn_diagonal_capture(color, attacker_pos, enemy_pos, expected_capture_pos):
    board = Board()
    pawn = Pawn(color)
    enemy = Pawn("black" if color == "white" else "white")
    board.place_piece(pawn, attacker_pos)
    board.place_piece(enemy, enemy_pos)
    moves = pawn.get_valid_moves(board)
    assert expected_capture_pos in moves


@pytest.mark.parametrize("attacker_color, attacker_pos, target_pos, last_move", [
    ("white", (3, 4), (2, 5), ((1, 5), (3, 5))),
    ("black", (4, 3), (5, 2), ((6, 2), (4, 2))),
])
def test_en_passant(attacker_color, attacker_pos, target_pos, last_move):
    board = Board()
    attacker = Pawn(attacker_color)
    defender_color = "black" if attacker_color == "white" else "white"
    defender = Pawn(defender_color)
    board.place_piece(attacker, attacker_pos)
    board.place_piece(defender, last_move[1])
    board.last_move = last_move
    moves = attacker.get_valid_moves(board)
    assert target_pos in moves


@pytest.mark.parametrize("color, start_row, promotion_row", [
    ("white", 1, 0),
    ("black", 6, 7),
])
def test_pawn_promotion(color, start_row, promotion_row):
    board = Board()
    pawn = Pawn(color)
    board.place_piece(pawn, (start_row, 0))
    board.move_piece((start_row, 0), (promotion_row, 0))
    promoted = board.get_piece_at((promotion_row, 0))
    from pieces import Queen
    assert isinstance(promoted, Queen)
    assert promoted.color == color


@pytest.mark.parametrize("color, start_row, promotion_row, piece_cls_name", [
    ("white", 1, 0, "Knight"),
    ("black", 6, 7, "Rook"),
])
def test_pawn_custom_promotion(color, start_row, promotion_row, piece_cls_name):
    board = Board()
    from pieces import Knight, Rook
    piece_map = {"Knight": Knight, "Rook": Rook}
    pawn = Pawn(color)
    board.place_piece(pawn, (start_row, 0))
    board.move_piece((start_row, 0), (promotion_row, 0), promotion_piece_cls=piece_map[piece_cls_name])
    promoted = board.get_piece_at((promotion_row, 0))
    assert isinstance(promoted, piece_map[piece_cls_name])
    assert promoted.color == color
