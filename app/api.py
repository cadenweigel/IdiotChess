from flask import Blueprint, jsonify, request
from app.game import GameManager
from app.bots import WhiteIdiotBot, BlackIdiotBot
from app.player import HumanPlayer

api = Blueprint("api", __name__)

# Global game instance
game = GameManager()

@api.route("/ping")
def ping():
    return jsonify({"message": "pong"})

@api.route("/start", methods=["POST"])
def start_game():
    data = request.get_json()
    mode = data.get("mode", "human_vs_bot")  # options: human_vs_bot, bot_vs_bot

    if mode == "bot_vs_bot":
        game.set_players(WhiteIdiotBot(), BlackIdiotBot())
    else:
        # Default: human vs bot (human is white)
        game.set_players(HumanPlayer("Player", "white"), BlackIdiotBot())

    return jsonify({"message": f"Game started in mode: {mode}."})

@api.route("/move", methods=["POST"])
def make_move():
    data = request.get_json()
    from_pos = tuple(data["from"])  # e.g., [6, 4]
    to_pos = tuple(data["to"])
    promotion = data.get("promotion")  # e.g., "Queen"

    promotion_cls = None
    if promotion == "Queen":
        from pieces import Queen
        promotion_cls = Queen
    elif promotion == "Rook":
        from pieces import Rook
        promotion_cls = Rook
    elif promotion == "Bishop":
        from pieces import Bishop
        promotion_cls = Bishop
    elif promotion == "Knight":
        from pieces import Knight
        promotion_cls = Knight

    success = game.make_move(from_pos, to_pos, promotion_piece_cls=promotion_cls)
    return jsonify({"success": success, "status": game.get_game_status()})

@api.route("/state")
def get_state():
    board_state = []
    for row in range(8):
        board_row = []
        for col in range(8):
            piece = game.board.get_piece_at((row, col))
            if piece:
                board_row.append({
                    "type": piece.__class__.__name__,
                    "color": piece.color,
                    "position": piece.position
                })
            else:
                board_row.append(None)
        board_state.append(board_row)

    return jsonify({
        "board": board_state,
        "turn": game.current_turn,
        "status": game.get_game_status()
    })

@api.route("/bot-move", methods=["POST"])
def bot_move():
    try:
        current_player = game.get_current_player()
        if not isinstance(current_player, (WhiteIdiotBot, BlackIdiotBot)):
            return jsonify({
                "success": False,
                "message": "It's not the bot's turn."
            }), 400

        move = current_player.decide_move(game.board)
        if move:
            from_pos, to_pos = move
            game.make_move(from_pos, to_pos)
            return jsonify({
                "success": True,
                "move": [from_pos, to_pos],
                "status": game.get_game_status()
            })
        return jsonify({
            "success": False,
            "message": "Bot has no valid moves."
        }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
