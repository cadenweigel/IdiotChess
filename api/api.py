from flask import Blueprint, request, jsonify
from api.game import GameManager
from api.player import HumanPlayer
from api.bots import WhiteIdiotBot, BlackIdiotBot
import uuid

api = Blueprint("api", __name__)  # ← NO url_prefix here

# Simple in-memory game registry
active_games = {}

@api.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "pong"})


@api.route("/start-game", methods=["POST"])
def start_game():
    data = request.get_json()
    bot_name = data.get("bot")

    if bot_name not in {"Wyatt", "Moose"}:
        return jsonify({"error": "Invalid bot selected"}), 400

    game_id = str(uuid.uuid4())
    game = GameManager()

    if bot_name == "Wyatt":
        white_player = WhiteIdiotBot()
        black_player = HumanPlayer(name="You", color="black")
    elif bot_name == "Moose":
        white_player = HumanPlayer(name="You", color="white")
        black_player = BlackIdiotBot()

    game.set_players(white_player, black_player)
    active_games[game_id] = game

    return jsonify({
        "message": f"Game started against {bot_name}",
        "game_id": game_id,
        "bot_color": white_player.color if isinstance(white_player, (WhiteIdiotBot, BlackIdiotBot)) else black_player.color
    })
