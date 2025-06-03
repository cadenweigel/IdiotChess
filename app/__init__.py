from flask import Flask
from .api import api
from .models import db
from .config import Config
import os
import json

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    app.register_blueprint(api)

    # Initialize games dictionary
    if "games" not in app.config:
        app.config["games"] = {}
        
    # Load saved games if they exist
    games_file = os.path.join(app.instance_path, 'games.json')
    if os.path.exists(games_file):
        try:
            with open(games_file, 'r') as f:
                saved_games = json.load(f)
                # Convert the saved games back to GameManager instances
                for session_id, game_data in saved_games.items():
                    from app.game import GameManager
                    manager = GameManager.from_dict(game_data)
                    app.config["games"][session_id] = manager
        except Exception as e:
            print(f"Error loading saved games: {e}")

    # Save games periodically
    @app.before_request
    def save_games():
        try:
            os.makedirs(app.instance_path, exist_ok=True)
            with open(games_file, 'w') as f:
                # Convert GameManager instances to serializable format
                games_data = {}
                for session_id, manager in app.config["games"].items():
                    games_data[session_id] = manager.to_dict()
                json.dump(games_data, f)
        except Exception as e:
            print(f"Error saving games: {e}")

    return app