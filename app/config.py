import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/idiotchess')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    
    # Game configuration
    GAME_SESSION_TIMEOUT = int(os.getenv('GAME_SESSION_TIMEOUT', '3600'))  # 1 hour default 