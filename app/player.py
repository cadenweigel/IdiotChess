import random
from app.board import Board

class Player:
    def __init__(self, name: str, color: str, image: str = None):
        self.name = name
        self.color = color  # 'white' or 'black'
        self.image = image  # Path to player avatar or image

    def decide_move(self, board):
        """
        Override this method for user or bot input.
        Should return a tuple: (from_position, to_position)
        """
        raise NotImplementedError("Subclasses must implement decide_move")

    def __repr__(self):
        return f"Player(name={self.name}, color={self.color})"

class HumanPlayer(Player):
    def __init__(self, name: str, color: str, image: str = None):
        super().__init__(name, color, image)

    def decide_move(self, board):
        """
        This method would typically be triggered by UI interaction.
        For now, it raises an error to signal it's user-driven.
        """
        raise RuntimeError("HumanPlayer move should come from UI input, not decide_move()")


