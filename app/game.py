from board import Board

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
