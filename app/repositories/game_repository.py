from abc import ABC, abstractmethod
from typing import Dict, Optional

from model.game import Game, GameStatus


class GameRepositoryInterface(ABC):
    """Abstract interface for game storage (DIP)."""

    @abstractmethod
    def save(self, game: Game) -> None:
        pass

    @abstractmethod
    def find_by_id(self, game_id: str) -> Optional[Game]:
        pass

    @abstractmethod
    def get_all_active_games(self) -> list[Game]:
        pass

    @abstractmethod
    def get_total_games_count(self) -> int:
        pass


class InMemoryGameRepository(GameRepositoryInterface):
    """In-memory implementation of game repository."""

    def __init__(self):
        self._games: Dict[str, Game] = {}

    def save(self, game: Game) -> None:
        self._games[game.id] = game

    def find_by_id(self, game_id: str) -> Optional[Game]:
        return self._games.get(game_id)

    def get_all_active_games(self) -> list[Game]:
        return [
            game for game in self._games.values()
            if game.status == GameStatus.ACTIVE
        ]

    def get_total_games_count(self) -> int:
        return len(self._games)
