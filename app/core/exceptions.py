
class GameNotFoundException(Exception):
    """Raised when a game is not found."""
    def __init__(self, game_id: str):
        self.game_id = game_id
        super().__init__(f"Game not found: {game_id}")


class GameNotActiveException(Exception):
    """Raised when trying to interact with a non-active game."""
    def __init__(self, game_id: str, status: str):
        self.game_id = game_id
        self.status = status
        super().__init__(f"Game {game_id} is not active (status: {status})")


class InvalidTurnException(Exception):
    """Raised when it's not the player's turn."""
    def __init__(self, player_name: str, current_player: str):
        self.player_name = player_name
        self.current_player = current_player
        super().__init__(f"Not {player_name}'s turn. Current player: {current_player}")


class WordValidationException(Exception):
    """Raised when word validation fails."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
