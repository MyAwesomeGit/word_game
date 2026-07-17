import uuid
from datetime import datetime
from typing import Optional, Tuple
import logging

from model.game import Game, GameStatus, Player, WordEntry
from services.word_service import WordValidator, WordProcessor
from core.exceptions import (
    GameNotActiveException,
    InvalidTurnException,
    WordValidationException
)


class GameService:
    """Core game business logic (SRP)."""

    def __init__(
            self,
            word_validator: WordValidator,
            word_processor: WordProcessor,
            game_id_length: int = 8
    ):
        self._word_validator = word_validator
        self._word_processor = word_processor
        self._game_id_length = game_id_length
        self._logger = logging.getLogger(__name__)

    def create_game(self, player1_name: str, player2_name: str) -> Game:
        """Create a new game instance."""
        game_id = str(uuid.uuid4())[:self._game_id_length]

        player1 = Player(name=player1_name)
        player2 = Player(name=player2_name)

        game = Game(
            id=game_id,
            player1=player1,
            player2=player2,
            current_player=player1,
            created_at=datetime.now().isoformat()
        )

        self._logger.info(f"Game created: {game_id} ({player1_name} vs {player2_name})")
        return game

    def validate_word_submission(
            self,
            word: str,
            game: Game,
            player_name: str
    ) -> None:
        """
        Validate a word submission.

        Raises:
            GameNotActiveException: If game is not active
            InvalidTurnException: If not player's turn
            WordValidationException: If word is invalid
        """
        # Check game status
        if game.status != GameStatus.ACTIVE:
            raise GameNotActiveException(game.id, game.status)

        # Check turn
        if player_name != game.current_player.name:
            raise InvalidTurnException(player_name, game.current_player.name)

        # Normalize word
        normalized_word = self._word_processor.normalize_word(word)

        # Validate length
        if not self._word_validator.is_valid_length(normalized_word):
            raise WordValidationException("Word is too short")

        # Validate starting letter
        if not self._word_validator.has_valid_start_letter(
                normalized_word,
                game.last_letter
        ):
            raise WordValidationException(
                f"Word must start with letter '{game.last_letter}'"
            )

        # Check if word already used
        if normalized_word in game.used_words:
            raise WordValidationException("Word already used")

        # Check dictionary
        if not self._word_validator.is_in_dictionary(normalized_word):
            raise WordValidationException("Word is too short (not in dictionary)")


    def process_word_submission(
            self,
            word: str,
            game: Game,
            player_name: str
    ) -> None:
        """Process a valid word submission."""
        normalized_word = self._word_processor.normalize_word(word)

        # Create word entry
        word_entry = WordEntry(
            word=normalized_word,
            player=player_name,
            timestamp=datetime.now().isoformat(),
            score_added=len(normalized_word)
        )

        # Update game state
        game.add_word(word_entry)
        game.last_letter = self._word_processor.get_next_start_letter(normalized_word)
        game.switch_turn()

        self._logger.info(
            f"Word '{normalized_word}' submitted by {player_name} "
            f"in game {game.id}"
        )

    def end_game(self, game: Game) -> dict:
        """End the game and return final results."""
        game.status = GameStatus.FINISHED
        winner = game.get_winner()

        self._logger.info(f"Game {game.id} ended. Winner: {winner}")

        return {
            "status": "finished",
            "winner": winner,
            "final_scores": {
                game.player1.name: game.player1.score,
                game.player2.name: game.player2.score
            }
        }

    def get_game_stats(self, game: Game) -> dict:
        """Get detailed statistics for a game."""
        return {
            "game_id": game.id,
            "created_at": game.created_at,
            "status": game.status,
            "player1": self._get_player_stats(game, game.player1),
            "player2": self._get_player_stats(game, game.player2),
            "total_words": len(game.used_words),
            "word_list": game.word_history
        }

    def _get_player_stats(self, game: Game, player: Player) -> dict:
        """Get statistics for a specific player."""
        player_words = [
            entry for entry in game.word_history
            if entry.player == player.name
        ]

        return {
            "name": player.name,
            "score": player.score,
            "words_count": len(player_words)
        }
