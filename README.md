# IdiotChess

A web-based chess game with multiple AI opponents of varying difficulty levels. Play against different chess bots, each with their own unique personality and playing style, or watch bots play against each other!

## Features

- Play chess against AI opponents with different personalities and skill levels
- Multiple bot types with varying strategies:
  - **Wyatt & Moose**: Random move bots (white and black respectively)
  - **Pongo**: Greedy bot that makes moves based on piece values
  - **Borzoi**: Uses 1-ply minimax algorithm
  - **Barrow of Monkeys**: Uses 2-ply minimax with mobility evaluation
  - **Gigantopithecus**: Uses 2-ply minimax with safety evaluation
- Watch bot vs bot matches
- Real-time game state updates
- Move validation and legal move highlighting
- Persistent game state storage
- Modern, responsive web interface

## Tech Stack

- **Backend**: Python/Flask
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **Testing**: Pytest
- **Database Migrations**: Alembic

## Prerequisites

- Python 3.x
- PostgreSQL
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/cadenweigel/IdiotChess.git
cd IdiotChess
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
DATABASE_URL=postgresql://username:password@localhost/idiotchess
FLASK_APP=run.py
FLASK_ENV=development
```

5. Initialize the database:
```bash
flask db upgrade
```

## Running the Application

1. Start the Flask development server:
```bash
flask run
```

2. Open your web browser and navigate to `http://localhost:5000`

## Running Tests

```bash
pytest
```

## Project Structure

```
IdiotChess/
├── app/                    # Main application package
│   ├── __init__.py        # Application factory
│   ├── api.py             # API routes and endpoints
│   ├── game.py            # Game logic
│   ├── player.py          # Player classes
│   ├── bots/              # Bot implementations
│   ├── models.py          # Database models
│   ├── static/            # Static files (CSS, JS, images)
│   └── templates/         # HTML templates
├── migrations/            # Database migrations
├── tests/                # Test suite
├── utils/                # Utility functions
├── pieces/              # Chess piece implementations
├── alembic.ini          # Alembic configuration
├── requirements.txt     # Project dependencies
└── run.py              # Application entry point
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.


