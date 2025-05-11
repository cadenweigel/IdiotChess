from . import create_app
from flask_cors import CORS
from dotenv import load_dotenv

app = create_app()
load_dotenv()
CORS(app)  # Allow all origins for dev

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)