from flask import Blueprint, jsonify, current_app, render_template

api = Blueprint("api", __name__)

@api.route("/")
def index():
    return render_template("index.html")

@api.route("/play")
def play():
    return render_template("play.html")

@api.route("/api/board", methods=["GET"])
def get_board_state():
    board = current_app.config["board"]
    board_state = []

    for row in board.grid:
        row_data = []
        for piece in row:
            row_data.append(piece.symbol() if piece else None)
        board_state.append(row_data)

    return jsonify({"board": board_state})
