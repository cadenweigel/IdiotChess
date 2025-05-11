import uuid
from flask import Blueprint, jsonify, current_app, render_template, request
from app.game import GameManager
from app.player import HumanPlayer
from app.bots import IdiotBot, WhiteIdiotBot, BlackIdiotBot

api = Blueprint("api", __name__)

BOT_REGISTRY = {
    "white_idiot": WhiteIdiotBot,
    "black_idiot": BlackIdiotBot,
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
    bot_color = data.get("bot_color", "black")  # default to black bot
    print(f"Creating new game with bot color: {bot_color}")

    session_id = str(uuid.uuid4())
    manager = GameManager()

    if bot_color == "white":
        print("Setting up white bot vs human")
        white_bot = WhiteIdiotBot()
        black_player = HumanPlayer(name="You", color="black")
        print(f"White bot: {white_bot}")
        print(f"Black player: {black_player}")
        manager.set_players(white_bot, black_player)
    elif bot_color == "black":
        print("Setting up human vs black bot")
        white_player = HumanPlayer(name="You", color="white")
        black_bot = BlackIdiotBot()
        print(f"White player: {white_player}")
        print(f"Black bot: {black_bot}")
        manager.set_players(white_player, black_bot)

    current_app.config["games"][session_id] = manager
    print(f"Game created with session ID: {session_id}")
    print(f"Initial turn: {manager.current_turn}")
    print(f"White player: {manager.players['white']}")
    print(f"Black player: {manager.players['black']}")
    
    return jsonify({"session_id": session_id})

@api.route("/api/new-game/bots", methods=["POST"])
def new_game_bots_only():
    data = request.get_json()
    white_key = data.get("white_bot", "white_idiot")
    black_key = data.get("black_bot", "black_idiot")

    white_bot_cls = BOT_REGISTRY.get(white_key)
    black_bot_cls = BOT_REGISTRY.get(black_key)

    if not white_bot_cls or not black_bot_cls:
        return jsonify({"error": "Invalid bot selection"}), 400

    session_id = str(uuid.uuid4())
    manager = GameManager()

    manager.set_players(
        white_bot_cls(),  # enforced white bot
        black_bot_cls()   # enforced black bot
    )

    current_app.config["games"][session_id] = manager
    return jsonify({"session_id": session_id})

@api.route("/api/bots", methods=["GET"])
def get_available_bots():
    return jsonify({
        "bots": [
            {"id": "white_idiot", "name": "Wyatt", "description": "Picks a random legal move. Plays white.", "avatar": "wyatt.png"},
            {"id": "black_idiot", "name": "Moose", "description": "Picks a random legal move. Plays black.", "avatar": "moose.png"}
            # later you can add more like:
            # {"id": "minimax", "name": "MinimaxBot"},
            # {"id": "chaotic", "name": "ChaoticBot"},
        ]
    })


@api.route("/api/board", methods=["GET"])
def get_board_state():
    session_id = request.args.get("session_id")
    manager = current_app.config["games"].get(session_id)
    if not manager:
        return jsonify({"error": "Invalid session ID"}), 400

    board = manager.board
    board_state = []

    for row in board.grid:
        row_data = []
        for piece in row:
            row_data.append(piece.symbol() if piece else None)
        board_state.append(row_data)

    return jsonify({"board": board_state, "turn": manager.current_turn, "status": manager.get_game_status()})

@api.route("/api/move", methods=["POST"])
def make_move():
    data = request.get_json()
    print("RAW JSON from request:", data)
    print("data.get('from') =", data.get("from"), "type:", type(data.get("from")))
    session_id = data.get("session_id")
    from_pos = tuple(map(int, data.get("from")))
    to_pos = tuple(map(int, data.get("to")))

    manager = current_app.config["games"].get(session_id)
    if not manager:
        return jsonify({"error": "Invalid session ID"}), 400
    print(f"from_pos = {from_pos}, to_pos = {to_pos}, type(from_pos) = {type(from_pos)}")
    success = manager.make_move(from_pos, to_pos)
    if not success:
        return jsonify({"error": "Invalid move"}), 400

    return jsonify({
        "success": True,
        "turn": manager.current_turn,
        "status": manager.get_game_status()
    })

@api.route("/api/bot-move", methods=["POST"])
def bot_move():
    """Make a move for the current bot player"""
    data = request.get_json()
    session_id = data.get('session_id')
    bot_color = data.get('bot_color')  # Get the bot color from the request
    
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
    
    try:
        # Get the bot's move using the board directly
        move = player.decide_move(manager.board)
        
        # If no move is found and we're in checkmate, return a special response
        if not move and manager.board.is_checkmate(player.color):
            return jsonify({
                'success': True,
                'status': 'checkmate',
                'winner': 'black' if player.color == 'white' else 'white'
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
            
        # Make the move by passing from_pos and to_pos separately
        success = manager.make_move(from_pos, to_pos)
        if not success:
            return jsonify({'error': 'Invalid move'}), 400
            
        # Get the updated board state
        board_state = []
        for row in manager.board.grid:
            row_data = []
            for piece in row:
                row_data.append(piece.symbol() if piece else None)
            board_state.append(row_data)
        
        return jsonify({
            'success': True,
            'move': {
                'from': [from_pos[0], from_pos[1]],
                'to': [to_pos[0], to_pos[1]]
            },
            'board': board_state,
            'status': manager.get_game_status()
        })
        
    except Exception as e:
        print(f"Error in bot_move: {str(e)}")
        return jsonify({'error': str(e)}), 500

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