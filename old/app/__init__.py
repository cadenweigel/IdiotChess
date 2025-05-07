from flask import Flask
from .api import api

def create_app():
    app = Flask(__name__)
    app.register_blueprint(api)

    # Safe place to initialize shared config
    if "games" not in app.config:
        app.config["games"] = {}

    return app