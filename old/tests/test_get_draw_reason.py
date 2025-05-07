import pytest
from app.board import Board
from pieces import King, Queen, Rook, Knight, Bishop, Pawn


@pytest.mark.parametrize("setup_func, expected_reason", [
    # Draw by stalemate
    (
        lambda: setup_stalemate(Board()),
        "stalemate"
    ),

    # Draw by insufficient material
    (
        lambda: setup_insufficient_material(Board()),
        "insufficient material"
    ),

    # Draw by 50-move rule
    (
        lambda: setup_fifty_move_rule(Board()),
        "50-move rule"
    ),

    # Draw by threefold repetition
    (
        lambda: setup_threefold_repetition(Board()),
        "threefold repetition"
    ),

    # No draw
    (
        lambda: setup_non_draw(Board()),
        None
    ),
])
def test_get_draw_reason(setup_func, expected_reason):
    board = setup_func()
    assert board.get_draw_reason("white") == expected_reason


# --- Setup Helpers --- #

def setup_stalemate(board: Board) -> Board:
    board.place_piece(King("white"), (7, 7))
    board.place_piece(Queen("black"), (6, 5))
    board.place_piece(King("black"), (5, 5))
    return board


def setup_insufficient_material(board: Board) -> Board:
    board.place_piece(King("white"), (7, 7))
    board.place_piece(Knight("white"), (6, 5))
    board.place_piece(King("black"), (0, 0))
    return board


def setup_fifty_move_rule(board: Board) -> Board:
    board.place_piece(King("white"), (7, 7))
    board.place_piece(King("black"), (0, 0))
    board.halfmove_clock = 100
    return board


def setup_threefold_repetition(board: Board) -> Board:
    board.place_piece(King("white"), (7, 7))
    board.place_piece(King("black"), (0, 0))
    board.place_piece(Knight("white"), (6, 5))

    for _ in range(3):
        board.move_piece((6, 5), (5, 3))
        board.move_piece((0, 0), (0, 0))  # black no-op
        board.move_piece((5, 3), (6, 5))
        board.move_piece((0, 0), (0, 0))

    return board


def setup_non_draw(board: Board) -> Board:
    board.place_piece(King("white"), (7, 7))
    board.place_piece(King("black"), (0, 0))
    board.place_piece(Pawn("white"), (6, 0))
    board.halfmove_clock = 10
    return board
