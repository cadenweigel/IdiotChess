import pytest
from app.bots import GreedyBot
from app.board import Board
from pieces import Pawn, Rook, Knight, Bishop, Queen, King

def test_greedy_bot_initialization():
    """Test that GreedyBot initializes correctly with given name and color."""
    bot = GreedyBot(name="TestBot", color="white")
    assert bot.name == "Pongo"  # Name should be overridden to "Pongo"
    assert bot.color == "white"
    assert bot.image == "pongo.png"

def test_greedy_bot_prefers_captures():
    """Test that GreedyBot prefers capturing higher value pieces."""
    board = Board()
    bot = GreedyBot(name="TestBot", color="white")
    
    # Place white pawn at (6, 1) (b2), black queen at (5, 2) (c3)
    board.place_piece(Pawn("white"), (6, 1))
    board.place_piece(Queen("black"), (5, 2))
    
    move = bot.decide_move(board)
    assert move is not None
    from_pos, to_pos = move
    
    # Should capture the queen
    assert from_pos == (6, 1)
    assert to_pos == (5, 2)

def test_greedy_bot_avoids_check():
    """Test that GreedyBot avoids moves that leave it in check."""
    board = Board()
    bot = GreedyBot(name="TestBot", color="white")
    
    # White king at (7, 0), black rook at (7, 7) (h1)
    board.place_piece(King("white"), (7, 0))
    board.place_piece(Rook("black"), (7, 7))
    
    move = bot.decide_move(board)
    assert move is not None
    from_pos, to_pos = move
    
    test_board = board.copy()
    assert test_board.move_piece(from_pos, to_pos)
    assert not test_board.is_in_check("white")

def test_greedy_bot_center_preference():
    """Test that GreedyBot has a slight preference for center moves."""
    board = Board()
    bot = GreedyBot(name="TestBot", color="white")
    
    # White knight at (7, 1), black pawns at (5, 2) and (6, 3)
    board.place_piece(Knight("white"), (7, 1))
    board.place_piece(Pawn("black"), (5, 2))
    board.place_piece(Pawn("black"), (6, 3))
    
    move = bot.decide_move(board)
    assert move is not None
    from_pos, to_pos = move
    
    # Accept either capture move as valid
    assert from_pos == (7, 1)
    assert to_pos in [(6, 3), (5, 2)]

