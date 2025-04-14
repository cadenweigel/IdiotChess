from flask import Flask
from .api import api
from .board import Board

def create_app():
    app = Flask(__name__)

    # Create and set up the board
    board = Board()
    board.setup_standard_position()
    app.config["board"] = board

    # Register routes
    app.register_blueprint(api)

    return app
