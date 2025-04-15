import uuid
from flask import Blueprint, jsonify, current_app, render_template, request
from app.game import GameManager
from app.player import HumanPlayer
from app.bots import IdiotBot

api = Blueprint("api", __name__)

@api.route("/")
def index():
    return render_template("index.html")

@api.route("/play")
def play():
    return render_template("play.html")

@api.route("/api/new-game/bot", methods=["POST"])
def new_game_vs_bot():
    session_id = str(uuid.uuid4())
    manager = GameManager()

    manager.set_players(
        HumanPlayer(name="You", color="white"),
        IdiotBot(name="Bot", color="black")
    )

    current_app.config["games"][session_id] = manager
    return jsonify({"session_id": session_id})

@api.route("/api/new-game/bots", methods=["POST"])
def new_game_bots_only():
    session_id = str(uuid.uuid4())
    manager = GameManager()

    manager.set_players(
        IdiotBot(name="Wyatt", color="white"),
        IdiotBot(name="Moose", color="black")
    )

    current_app.config["games"][session_id] = manager
    return jsonify({"session_id": session_id})

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
    session_id = data.get("session_id")
    from_pos = tuple(data.get("from"))
    to_pos = tuple(data.get("to"))

    manager = current_app.config["games"].get(session_id)
    if not manager:
        return jsonify({"error": "Invalid session ID"}), 400

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
    data = request.get_json()
    session_id = data.get("session_id")

    manager = current_app.config["games"].get(session_id)
    if not manager:
        return jsonify({"error": "Invalid session ID"}), 400

    player = manager.get_current_player()
    move = player.decide_move(manager.board)
    if not move:
        return jsonify({"error": "No valid moves for current player"}), 400

    from_pos, to_pos = move
    manager.make_move(from_pos, to_pos)

    return jsonify({
        "success": True,
        "from": from_pos,
        "to": to_pos,
        "turn": manager.current_turn,
        "status": manager.get_game_status()
    })

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