from app.board import Board
from app.player import HumanPlayer
from app.bots import WhiteIdiotBot, BlackIdiotBot

class GameManager:
    def __init__(self):
        self.board = Board()
        self.board.setup_standard_position()
        self.current_turn = 'white'
        self.players = {'white': None, 'black': None}

    def set_players(self, white_player, black_player):
        self.players['white'] = white_player
        self.players['black'] = black_player

    def get_current_player(self):
        return self.players[self.current_turn]

    def switch_turn(self):
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

    def is_game_over(self):
        return self.board.is_checkmate(self.current_turn) or self.board.is_draw(self.current_turn)

    def get_game_status(self):
        if self.board.is_checkmate(self.current_turn):
            return f"Checkmate! {self.opposite_color(self.current_turn).capitalize()} wins."
        elif self.board.is_draw(self.current_turn):
            reason = self.board.get_draw_reason(self.current_turn)
            return f"Draw by {reason}."
        elif self.board.is_in_check(self.current_turn):
            return f"{self.current_turn.capitalize()} is in check."
        return "Game ongoing."

    def make_move(self, from_pos, to_pos, promotion_piece_cls=None):
        piece = self.board.get_piece_at(from_pos)
        if not piece or piece.color != self.current_turn:
            return False

        success = self.board.move_piece(from_pos, to_pos, promotion_piece_cls=promotion_piece_cls)
        if success:
            self.switch_turn()
        return success

    def get_valid_moves(self, position):
        piece = self.board.get_piece_at(position)
        if piece and piece.color == self.current_turn:
            return piece.get_valid_moves(self.board)
        return []

    def opposite_color(self, color):
        return 'black' if color == 'white' else 'white'

    def print_board(self):
        self.board.print_board()

    def to_dict(self):
        """Convert game state to a dictionary for serialization"""
        # Convert board to serializable format
        board_state = []
        for row in self.board.grid:
            row_data = []
            for piece in row:
                if piece is None:
                    row_data.append(None)
                else:
                    row_data.append({
                        'type': piece.__class__.__name__,
                        'color': piece.color,
                        'symbol': piece.symbol()
                    })
            board_state.append(row_data)

        return {
            'board': board_state,
            'current_turn': self.current_turn,
            'players': {
                'white': {
                    'type': 'human' if isinstance(self.players['white'], HumanPlayer) else 'bot',
                    'name': self.players['white'].name,
                    'color': self.players['white'].color
                },
                'black': {
                    'type': 'human' if isinstance(self.players['black'], HumanPlayer) else 'bot',
                    'name': self.players['black'].name,
                    'color': self.players['black'].color
                }
            }
        }

    @classmethod
    def from_dict(cls, data):
        """Create a GameManager instance from a dictionary"""
        manager = cls()
        manager.current_turn = data['current_turn']
        
        # Restore board state
        from pieces import Pawn, Rook, Knight, Bishop, Queen, King
        piece_classes = {
            'Pawn': Pawn,
            'Rook': Rook,
            'Knight': Knight,
            'Bishop': Bishop,
            'Queen': Queen,
            'King': King
        }
        
        for row in range(8):
            for col in range(8):
                piece_data = data['board'][row][col]
                if piece_data:
                    piece_class = piece_classes[piece_data['type']]
                    piece = piece_class(piece_data['color'])
                    manager.board.place_piece(piece, (row, col))

        # Restore players
        white_data = data['players']['white']
        black_data = data['players']['black']

        if white_data['type'] == 'human':
            manager.players['white'] = HumanPlayer(name=white_data['name'], color=white_data['color'])
        else:
            manager.players['white'] = WhiteIdiotBot()

        if black_data['type'] == 'human':
            manager.players['black'] = HumanPlayer(name=black_data['name'], color=black_data['color'])
        else:
            manager.players['black'] = BlackIdiotBot()

        return manager
