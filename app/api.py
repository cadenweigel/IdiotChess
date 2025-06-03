import uuid
import copy
import random
from flask import Blueprint, jsonify, current_app, render_template, request
from app.game import GameManager
from app.player import HumanPlayer
from app.bots import IdiotBot, WhiteIdiotBot, BlackIdiotBot, GreedyBot, MinimaxBot, BetterMinimaxBotOne, BetterMinimaxBotTwo
from app.models import db, Game, BoardState, Move
from datetime import datetime, UTC, timedelta

api = Blueprint("api", __name__)

BOT_REGISTRY = {
    "white_idiot": WhiteIdiotBot,
    "black_idiot": BlackIdiotBot,
    "pongo": GreedyBot,
    "borzoi": MinimaxBot,
    "barrowofmonkeys": BetterMinimaxBotOne,
    "gigantopithecus": BetterMinimaxBotTwo,
    # Add others here
}

@api.route("/")
def index():
    return render_template("index.html")

@api.route("/play")
def play():
    return render_template("play.html")

@api.route("/api/new-game/bot", methods=["POST"])
def new_game_vs_bot():
    data = request.get_json()
    bot_type = data.get("bot_type", "black_idiot")
    player_color = data.get("player_color", "random")
    player_name = data.get("player_name", "default")
    
    # For Pongo or when player chooses random, randomly choose the color
    if bot_type == "pongo" or player_color == "random":
        bot_color = random.choice(["white", "black"])
    else:
        # For fixed-color bots or when player has a preference
        if bot_type == "white_idiot":
            bot_color = "white"
        elif bot_type == "black_idiot":
            bot_color = "black"
        else:
            # For other bots when player has a color preference
            bot_color = "black" if player_color == "white" else "white"
    
    print(f"Creating new game with bot color: {bot_color}")

    session_id = uuid.uuid4()  # Use UUID object directly for database
    manager = GameManager()

    bot_cls = BOT_REGISTRY.get(bot_type)
    if not bot_cls:
        return jsonify({"error": "Invalid bot type"}), 400

    try:
        # Set up players
        if bot_color == "white":
            print("Setting up white bot vs human")
            white_bot = bot_cls(name=bot_cls.__name__, color="white")
            black_player = HumanPlayer(name=player_name, color="black")
            print(f"White bot: {white_bot}")
            print(f"Black player: {black_player}")
            manager.set_players(white_bot, black_player)
            white_type = "bot"
            white_name = bot_cls.__name__
            black_type = "human"
            black_name = player_name
        else:
            print("Setting up human vs black bot")
            white_player = HumanPlayer(name=player_name, color="white")
            black_bot = bot_cls(name=bot_cls.__name__, color="black")
            print(f"White player: {white_player}")
            print(f"Black bot: {black_bot}")
            manager.set_players(white_player, black_bot)
            white_type = "human"
            white_name = player_name
            black_type = "bot"
            black_name = bot_cls.__name__

        # Create game record in database
        game = Game(
            session_id=session_id,
            current_turn=manager.current_turn,
            game_status="active",
            white_player_type=white_type,
            black_player_type=black_type,
            white_player_name=white_name,
            black_player_name=black_name
        )
        db.session.add(game)

        # Save initial board state
        initial_board_state = BoardState(
            session_id=session_id,
            move_number=0,
            board_state=manager.to_dict()['board'],
            captured_pieces=[]
        )
        db.session.add(initial_board_state)

        # Commit the transaction
        db.session.commit()

        # Keep in-memory copy for active game
        current_app.config["games"][str(session_id)] = manager

        print(f"Game created with session ID: {session_id}")
        print(f"Initial turn: {manager.current_turn}")
        print(f"White player: {manager.players['white']}")
        print(f"Black player: {manager.players['black']}")
        
        return jsonify({"session_id": str(session_id), "bot_color": bot_color})
    except Exception as e:
        db.session.rollback()
        print(f"Error creating game: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api.route("/api/new-game/bots", methods=["POST"])
def new_game_bots_only():
    data = request.get_json()
    white_key = data.get("white_bot", "white_idiot")
    black_key = data.get("black_bot", "black_idiot")

    white_bot_cls = BOT_REGISTRY.get(white_key)
    black_bot_cls = BOT_REGISTRY.get(black_key)

    if not white_bot_cls or not black_bot_cls:
        return jsonify({"error": "Invalid bot selection"}), 400

    session_id = uuid.uuid4()
    manager = GameManager()

    # Instantiate bots with names and colors
    white_bot = white_bot_cls(name=white_bot_cls.__name__, color="white")
    black_bot = black_bot_cls(name=black_bot_cls.__name__, color="black")
    manager.set_players(white_bot, black_bot)

    # Save to database
    try:
        game = Game(
            session_id=session_id,
            current_turn=manager.current_turn,
            game_status="active",
            white_player_type="bot",
            black_player_type="bot",
            white_player_name=white_bot_cls.__name__,
            black_player_name=black_bot_cls.__name__
        )
        db.session.add(game)

        initial_board_state = BoardState(
            session_id=session_id,
            move_number=0,
            board_state=manager.to_dict()['board'],
            captured_pieces=[]
        )
        db.session.add(initial_board_state)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating bot vs bot game: {str(e)}")
        return jsonify({"error": str(e)}), 500

    # Keep in-memory copy for active game
    current_app.config["games"][str(session_id)] = manager
    return jsonify({"session_id": str(session_id)})

@api.route("/api/bots", methods=["GET"])
def get_available_bots():
    return jsonify({
        "bots": [
            {"id": "white_idiot", "name": "Wyatt", "description": "Picks a random legal move. Plays white.", "avatar": "wyatt.png"},
            {"id": "black_idiot", "name": "Moose", "description": "Picks a random legal move. Plays black.", "avatar": "moose.png"},
            {"id": "pongo", "name": "Pongo", "description": "Picks the best move by piece value.", "avatar": "pongo.png"},
            {"id": "borzoi", "name": "Borzoi", "description": "Uses 1-ply minimax to find the best move.", "avatar": "borzoi.png"},
            {"id": "barrowofmonkeys", "name": "Barrow of Monkeys", "description": "Uses 2-ply minimax with mobility evaluation.", "avatar": "barrowofmonkeys.png"},
            {"id": "gigantopithecus", "name": "Gigantopithecus", "description": "Uses 2-ply minimax with safety evaluation.", "avatar": "gigantopithecus.png"}
        ]
    })

def piece_to_dict(piece):
    """Convert a piece object to a dictionary representation"""
    if piece is None:
        return None
    return {
        'type': piece.__class__.__name__,
        'color': piece.color,
        'symbol': piece.symbol()
    }

@api.route("/api/board")
def get_board():
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'error': 'Missing session ID'}), 400

    try:
        session_id = uuid.UUID(session_id)
    except ValueError:
        return jsonify({'error': 'Invalid session ID format'}), 400

    # Try to get game from memory first
    manager = current_app.config["games"].get(str(session_id))
    
    # If not in memory, try to load from database
    if not manager:
        game = Game.query.get(session_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404

        # Get the latest board state
        latest_board_state = BoardState.query.filter_by(
            session_id=session_id
        ).order_by(BoardState.move_number.desc()).first()

        if not latest_board_state:
            return jsonify({'error': 'No board state found'}), 404

        # Create new game manager
        manager = GameManager()
        
        # Restore board state
        from app.pieces import Pawn, Rook, Knight, Bishop, Queen, King
        piece_classes = {
            'Pawn': Pawn,
            'Rook': Rook,
            'Knight': Knight,
            'Bishop': Bishop,
            'Queen': Queen,
            'King': King
        }
        
        for row in range(8):
            for col in range(8):
                piece_data = latest_board_state.board_state[row][col]
                if piece_data:
                    piece_class = piece_classes[piece_data['type']]
                    piece = piece_class(piece_data['color'])
                    manager.board.place_piece(piece, (row, col))

        # Restore players
        if game.white_player_type == 'human':
            manager.players['white'] = HumanPlayer(name=game.white_player_name, color='white')
        else:
            bot_cls = BOT_REGISTRY.get(game.white_player_name.lower().replace(' ', ''))
            if bot_cls:
                manager.players['white'] = bot_cls(name=game.white_player_name, color='white')
            else:
                manager.players['white'] = WhiteIdiotBot()

        if game.black_player_type == 'human':
            manager.players['black'] = HumanPlayer(name=game.black_player_name, color='black')
        else:
            bot_cls = BOT_REGISTRY.get(game.black_player_name.lower().replace(' ', ''))
            if bot_cls:
                manager.players['black'] = bot_cls(name=game.black_player_name, color='black')
            else:
                manager.players['black'] = BlackIdiotBot()

        # Restore game state
        manager.current_turn = game.current_turn

        # Restore move history
        moves = Move.query.filter_by(session_id=session_id).order_by(Move.move_number).all()
        manager.move_history = [
            {
                'from': move.from_position,
                'to': move.to_position,
                'color': move.piece_color
            }
            for move in moves
        ]

        # Store in memory for future requests
        current_app.config["games"][str(session_id)] = manager
    
    # Convert board state to a format the client can understand
    board_state = []
    for row in manager.board.grid:
        row_data = []
        for piece in row:
            if piece is None:
                row_data.append(None)
            else:
                row_data.append({
                    'type': piece.__class__.__name__,
                    'color': piece.color,
                    'symbol': piece.symbol()
                })
        board_state.append(row_data)
    
    # Get captured pieces
    captured_pieces = manager.board.get_captured_pieces_unicode()
    
    return jsonify({
        'board': board_state,
        'turn': manager.current_turn,
        'move_history': manager.move_history,
        'status': manager.get_game_status(),
        'captured_by_white': captured_pieces['captured_by_white'],
        'captured_by_black': captured_pieces['captured_by_black'],
        'white_player_name': manager.players['white'].name,
        'black_player_name': manager.players['black'].name
    })

@api.route("/api/move", methods=["POST"])
def make_move():
    data = request.get_json()
    print("RAW JSON from request:", data)
    print("data.get('from') =", data.get("from"), "type:", type(data.get("from")))
    session_id = uuid.UUID(data.get("session_id"))  # Convert string to UUID
    from_pos = tuple(map(int, data.get("from")))
    to_pos = tuple(map(int, data.get("to")))

    # Get game from database
    game = Game.query.get(session_id)
    if not game:
        return jsonify({"error": "Invalid session ID"}), 400

    # Get game manager from memory
    manager = current_app.config["games"].get(str(session_id))
    if not manager:
        return jsonify({"error": "Game not found in memory"}), 400

    print(f"from_pos = {from_pos}, to_pos = {to_pos}, type(from_pos) = {type(from_pos)}")
    
    # Get the piece being moved
    piece = manager.board.get_piece_at(from_pos)
    if not piece:
        return jsonify({"error": "No piece at selected position"}), 400
    
    # Check if it's the player's turn
    if piece.color != manager.current_turn:
        return jsonify({"error": "Not your turn"}), 400
    
    # Check if the move is in the piece's valid moves
    if to_pos not in piece.get_valid_moves(manager.board):
        return jsonify({"error": "Invalid move for this piece"}), 400
    
    # Check if the move would leave the king in check
    test_board = copy.deepcopy(manager.board)
    if test_board.move_piece(from_pos, to_pos, validate=False) and test_board.is_in_check(piece.color):
        return jsonify({"error": "This move would leave your king in check"}), 400
    
    # If we're in check, verify this move gets us out of check
    if manager.board.is_in_check(piece.color):
        test_board = copy.deepcopy(manager.board)
        if not test_board.move_piece(from_pos, to_pos, validate=False) or test_board.is_in_check(piece.color):
            return jsonify({"error": "You must move out of check"}), 400
    
    try:
        # Make the move in memory
        success = manager.make_move(from_pos, to_pos)
        if not success:
            return jsonify({"error": "Invalid move"}), 400

        # Get the current move number
        move_number = len(manager.move_history)

        # Save move to database
        move = Move(
            session_id=session_id,
            move_number=move_number,
            from_position=list(from_pos),  # Convert tuple to list for array storage
            to_position=list(to_pos),      # Convert tuple to list for array storage
            piece_type=piece.__class__.__name__,
            piece_color=piece.color
        )
        db.session.add(move)

        # Save new board state
        board_state = BoardState(
            session_id=session_id,
            move_number=move_number,
            board_state=manager.to_dict()['board'],
            captured_pieces=manager.board.get_captured_pieces_unicode()
        )
        db.session.add(board_state)

        # Update game status
        game.current_turn = manager.current_turn
        game.game_status = manager.get_game_status()
        game.last_active = datetime.now(UTC)

        # Commit all changes
        db.session.commit()

        return jsonify({
            "success": True,
            "turn": manager.current_turn,
            "status": manager.get_game_status()
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error making move: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api.route("/api/bot-move", methods=["POST"])
def bot_move():
    """Make a move for the current bot player"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        session_id = data.get('session_id')
        bot_color = data.get('bot_color')
        
        if not session_id:
            return jsonify({'error': 'Missing session ID'}), 400
            
        manager = current_app.config["games"].get(session_id)
        if not manager:
            return jsonify({'error': 'Invalid session ID'}), 400
            
        player = manager.get_current_player()
        print(f"Current turn: {manager.current_turn}")
        print(f"Current player: {player}")
        print(f"Player color: {player.color}")
        print(f"Requested bot color: {bot_color}")
        
        # Check if the current player is a bot
        if not hasattr(player, 'decide_move'):
            return jsonify({'error': 'Current player is human, not a bot'}), 400
            
        # Verify the bot color matches the current player's color
        if bot_color and player.color != bot_color:
            print(f"Bot color mismatch: Expected {bot_color}, got {player.color}")
            print(f"Current turn: {manager.current_turn}")
            print(f"Player type: {type(player)}")
            return jsonify({'error': f'Bot color mismatch. Expected {bot_color}, got {player.color}'}), 400
        
        # Get the bot's move using the board directly
        move = player.decide_move(manager.board)
        
        # If no move is found and we're in checkmate or draw, update DB and return
        if not move and (manager.board.is_checkmate(player.color) or manager.board.is_draw(player.color)):
            game = Game.query.get(uuid.UUID(session_id))
            if game:
                # Use manager.get_game_status() for a descriptive status
                game.game_status = manager.get_game_status()
                game.last_active = datetime.now(UTC)
                db.session.commit()
            return jsonify({
                'success': True,
                'status': manager.get_game_status(),
                'winner': 'black' if player.color == 'white' else 'white' if manager.board.is_checkmate(player.color) else None
            })
        
        if not move:
            return jsonify({'error': 'No valid move found'}), 400
            
        # Handle both tuple and Move object returns
        if isinstance(move, tuple):
            from_pos, to_pos = move
        else:
            from_pos = move.from_pos
            to_pos = move.to_pos
        
        print(f"Bot move: from {from_pos} to {to_pos}")
        
        # Get the piece symbol before making the move
        piece_obj = manager.board.get_piece_at(from_pos)
        if not piece_obj:
            return jsonify({'error': 'No piece found at move source position'}), 400
            
        piece_symbol = piece_obj.symbol()
        
        # Make the move by passing from_pos and to_pos separately
        success = manager.make_move(from_pos, to_pos)
        if not success:
            return jsonify({'error': 'Invalid move'}), 400
        
        # Get the updated board state
        board_state = []
        for row in manager.board.grid:
            row_data = []
            for piece in row:
                if piece is None:
                    row_data.append(None)
                else:
                    row_data.append(piece.symbol())
            board_state.append(row_data)
        
        # Get captured pieces
        captured_pieces = manager.board.get_captured_pieces_unicode()
        
        game = Game.query.get(uuid.UUID(session_id))
        if game:
            game.last_active = datetime.now(UTC)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'move': {
                'from': [from_pos[0], from_pos[1]],
                'to': [to_pos[0], to_pos[1]],
                'piece': piece_symbol
            },
            'board': board_state,
            'turn': manager.current_turn,
            'status': manager.get_game_status(),
            'captured_by_white': captured_pieces['captured_by_white'],
            'captured_by_black': captured_pieces['captured_by_black']
        })
        
    except Exception as e:
        print(f"Error in bot_move: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@api.route("/api/valid-moves", methods=["GET"])
def get_valid_moves():
    session_id = request.args.get("session_id")
    position = request.args.get("position")

    if not position:
        return jsonify({"error": "Missing piece position"}), 400

    try:
        row, col = map(int, position.split(","))
    except Exception:
        return jsonify({"error": "Invalid position format. Use 'row,col'."}), 400

    manager = current_app.config["games"].get(session_id)
    if not manager:
        return jsonify({"error": "Invalid session ID"}), 400

    moves = manager.get_valid_moves((row, col))
    return jsonify({"valid_moves": moves})

@api.route("/botvbot")
def botvbot_page():
    return render_template("botvbot.html")

@api.route("/api/resign", methods=["POST"])
def resign_game():
    data = request.get_json()
    session_id = data.get("session_id")
    resigning_color = data.get("resigning_color")
    if not session_id or not resigning_color:
        return jsonify({"error": "Missing session_id or resigning_color"}), 400
    try:
        session_id_uuid = uuid.UUID(session_id)
    except Exception:
        return jsonify({"error": "Invalid session_id format"}), 400

    # Update in-memory game manager if present
    manager = current_app.config["games"].get(str(session_id))
    if manager:
        # Optionally, you could set a flag or status in the manager
        pass

    # Update database
    game = Game.query.get(session_id_uuid)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    game.game_status = f"Resigned by {resigning_color}"
    game.last_active = datetime.now(UTC)
    db.session.commit()
    return jsonify({"success": True, "status": game.game_status})

@api.route("/api/cleanup-abandoned", methods=["POST"])
def cleanup_abandoned():
    timeout_minutes = int(request.json.get("timeout", 60))
    cutoff = datetime.now(UTC) - timedelta(minutes=timeout_minutes)
    abandoned_games = Game.query.filter(
        Game.game_status == "active",
        Game.last_active < cutoff
    ).all()
    count = len(abandoned_games)
    for game in abandoned_games:
        db.session.delete(game)
    db.session.commit()
    return jsonify({"deleted": count})