import pytest
from sqlalchemy import inspect, create_engine
from sqlalchemy.orm import sessionmaker
from app.config import Config
from app.models import Game, BoardState, db

@pytest.fixture(scope="session")
def engine():
    """Fixture to create a SQLAlchemy engine (using the DATABASE_URL from Config)."""
    return create_engine(Config.SQLALCHEMY_DATABASE_URI)


@pytest.fixture(scope="session")
def inspector(engine):
    """Fixture to create an inspector (from SQLAlchemy) for the engine."""
    return inspect(engine)


@pytest.fixture(scope="session")
def Session(engine):
    """Fixture to create a session factory (using the engine)."""
    return sessionmaker(bind=engine)


@pytest.fixture(scope="function")
def session(Session):
    """Fixture to create a session (using the Session factory) and rollback (or close) after each test."""
    sess = Session()
    yield sess
    sess.rollback()
    sess.close()


@pytest.mark.parametrize("table_name", ["games", "board_states", "moves"])
def test_table_exists(inspector, table_name):
    """Test that the given table exists in the database (in the 'public' schema)."""
    assert inspector.has_table(table_name, schema="public"), f"Table {table_name} does not exist."


def test_insert_and_query_game(session):
    """Insert a dummy game record and then query it (using a session)."""
    dummy_game = Game(current_turn="white", game_status="active", white_player_type="human", black_player_type="bot", white_player_name="Player", black_player_name="Bot")
    session.add(dummy_game)
    session.commit()
    queried_game = session.query(Game).filter_by(white_player_name="Player").one_or_none()
    assert queried_game is not None, "Inserted game not found."
    assert queried_game.current_turn == "white", "Expected current_turn to be 'white'."
    session.delete(queried_game)
    session.commit()


def test_board_states_relation(session):
    """Insert a dummy board state (with a foreign key to a game) and then query it (using a session)."""
    dummy_game = Game(current_turn="black", game_status="active", white_player_type="human", black_player_type="bot", white_player_name="Player", black_player_name="Bot")
    session.add(dummy_game)
    session.commit()
    dummy_board_state = BoardState(session_id=dummy_game.session_id, move_number=1, board_state={"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"}, captured_pieces=[])
    session.add(dummy_board_state)
    session.commit()
    queried_board_state = session.query(BoardState).filter_by(session_id=dummy_game.session_id, move_number=1).one_or_none()
    assert queried_board_state is not None, "Inserted board state not found."
    assert queried_board_state.board_state["fen"] == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "Expected board_state['fen'] to match."
    session.delete(queried_board_state)
    session.delete(dummy_game)
    session.commit() 