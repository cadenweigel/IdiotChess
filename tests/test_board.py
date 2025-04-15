
import pytest
from app.board import Board
from pieces import Pawn, Rook, Knight, Bishop, Queen, King


def test_board_starts_empty():
    board = Board()
    for row in board.grid:
        for cell in row:
            assert cell is None


@pytest.mark.parametrize("piece_cls, position", [
    (Pawn, (6, 4)),
    (Rook, (0, 0)),
    (Knight, (7, 1)),
])
def test_place_piece_sets_position(piece_cls, position):
    board = Board()
    piece = piece_cls("white")
    board.place_piece(piece, position)
    assert board.get_piece_at(position) is piece
    assert piece.position == position


@pytest.mark.parametrize("piece_cls, position", [
    (Rook, (0, 0)),
    (Knight, (5, 5)),
])
def test_remove_piece_clears_position_and_adds_to_captured(piece_cls, position):
    board = Board()
    piece = piece_cls("black")
    board.place_piece(piece, position)
    board.remove_piece(position)
    assert board.get_piece_at(position) is None
    assert piece in board.get_captured_pieces()
    assert piece.position is None


def test_move_piece_updates_board_and_position():
    board = Board()
    knight = Knight("white")
    board.place_piece(knight, (7, 1))
    moved = board.move_piece((7, 1), (5, 2))
    assert moved is True
    assert board.get_piece_at((5, 2)) is knight
    assert board.get_piece_at((7, 1)) is None
    assert knight.position == (5, 2)


@pytest.mark.parametrize("position, piece_cls", [
    ((0, 0), Rook),
    ((0, 4), King),
    ((6, 0), Pawn),
    ((7, 3), Queen),
])
def test_setup_standard_position_places_all_pieces(position, piece_cls):
    board = Board()
    board.setup_standard_position()
    assert isinstance(board.get_piece_at(position), piece_cls)

def test_standard_position_has_32_pieces_and_center_empty():
    board = Board()
    board.setup_standard_position()
    piece_count = sum(1 for row in board.grid for p in row if p is not None)
    assert piece_count == 32
    assert board.get_piece_at((3, 3)) is None
