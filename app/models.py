from datetime import datetime, UTC
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

db = SQLAlchemy()

class Game(db.Model):
    __tablename__ = 'games'
    
    session_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))
    current_turn = db.Column(db.String(5), nullable=False)
    game_status = db.Column(db.String(50), nullable=False)
    white_player_type = db.Column(db.String(20), nullable=False)
    black_player_type = db.Column(db.String(20), nullable=False)
    white_player_name = db.Column(db.String(100))
    black_player_name = db.Column(db.String(100))
    
    # Relationships
    board_states = db.relationship('BoardState', backref='game', lazy=True)
    moves = db.relationship('Move', backref='game', lazy=True)
    
    def to_dict(self):
        """Convert game to dictionary format"""
        return {
            'session_id': str(self.session_id),
            'created_at': self.created_at.isoformat(),
            'current_turn': self.current_turn,
            'game_status': self.game_status,
            'players': {
                'white': {
                    'type': self.white_player_type,
                    'name': self.white_player_name
                },
                'black': {
                    'type': self.black_player_type,
                    'name': self.black_player_name
                }
            }
        }

class BoardState(db.Model):
    __tablename__ = 'board_states'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('games.session_id'), nullable=False)
    move_number = db.Column(db.Integer, nullable=False)
    board_state = db.Column(JSONB, nullable=False)
    captured_pieces = db.Column(JSONB)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))
    
    def to_dict(self):
        """Convert board state to dictionary format"""
        return {
            'id': self.id,
            'session_id': str(self.session_id),
            'move_number': self.move_number,
            'board_state': self.board_state,
            'captured_pieces': self.captured_pieces,
            'created_at': self.created_at.isoformat()
        }

class Move(db.Model):
    __tablename__ = 'moves'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(UUID(as_uuid=True), db.ForeignKey('games.session_id'), nullable=False)
    move_number = db.Column(db.Integer, nullable=False)
    from_position = db.Column(db.ARRAY(db.Integer), nullable=False)
    to_position = db.Column(db.ARRAY(db.Integer), nullable=False)
    piece_type = db.Column(db.String(20), nullable=False)
    piece_color = db.Column(db.String(5), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))
    
    def to_dict(self):
        """Convert move to dictionary format"""
        return {
            'id': self.id,
            'session_id': str(self.session_id),
            'move_number': self.move_number,
            'from': self.from_position,
            'to': self.to_position,
            'piece_type': self.piece_type,
            'piece_color': self.piece_color,
            'created_at': self.created_at.isoformat()
        } 