import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, Game, BoardState, Move

def wipe_database():
    """Wipe all game data from the database.
    
    This function will delete all records from the moves, board_states, and games tables
    in the correct order to respect foreign key constraints.
    """
    app = create_app()
    with app.app_context():
        try:
            # Delete in correct order to respect foreign key constraints
            print("Deleting moves...")
            Move.query.delete()
            print("Deleting board states...")
            BoardState.query.delete()
            print("Deleting games...")
            Game.query.delete()
            
            # Commit the changes
            db.session.commit()
            print("Successfully wiped all game data from the database!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error wiping database: {str(e)}")
            raise

if __name__ == "__main__":
    # Ask for confirmation
    response = input("WARNING: This will delete ALL game data from the database. Are you sure? (yes/no): ")
    if response.lower() == "yes":
        wipe_database()
    else:
        print("Operation cancelled.") 